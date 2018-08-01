// Copyright 2017 The go-ethereum Authors
// This file is part of the go-ethereum library.
//
// The go-ethereum library is free software: you can redistribute it and/or modify
// it under the terms of the GNU Lesser General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.
//
// The go-ethereum library is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
// GNU Lesser General Public License for more details.
//
// You should have received a copy of the GNU Lesser General Public License
// along with the go-ethereum library. If not, see <http://www.gnu.org/licenses/>.

// Package usbwallet implements support for USB hardware wallets.
package remotewallet

import (
   "fmt"
   "math/big"
   "sync"
   "time"
   "bytes"
   "encoding/hex"

   ethereum "github.com/ethereum/go-ethereum"
   "github.com/ethereum/go-ethereum/accounts"
   "github.com/ethereum/go-ethereum/common"
   "github.com/ethereum/go-ethereum/core/types"
   "github.com/ethereum/go-ethereum/log"
)

// Maximum time between wallet health checks 
const heartbeatCycle = 60 * time.Second

// driver defines the vendor specific functionality hardware wallets instances
// must implement to allow using them with the wallet lifecycle management.
type driver interface {
// Status returns a textual status to aid the user in the current state of the
// wallet. It also returns an error indicating any failure the wallet might have
// encountered.
Status() (string, error)

// Open initializes access to a wallet instance. The passphrase parameter may
// or may not be used by the implementation of a particular wallet instance.
Open(passphrase string) error

// Close releases any resources held by an open wallet instance.
Close() error

// Heartbeat performs a sanity check against the hardware wallet to see if it
// is still online and healthy.
Heartbeat() error

// Derive sends a derivation request to the USB device and returns the Ethereum
// address located on that path.
Derive(path accounts.DerivationPath) (common.Address, error)

//
// SignTx sends the transaction to the signing server and waits for the response
// Note that the user must have unlocked their account through the customer facing web app
// for the signing server to authorize the transaction
//
SignTx(account accounts.Account, tx *types.Transaction, chainID *big.Int) (common.Address, *types.Transaction, error)

ReadAccounts() ([]accounts.Account, error)

}   // driver interface

// wallet represents the common functionality shared by all USB hardware
// wallets to prevent reimplementing the same complex maintenance mechanisms
// for different vendors.
type wallet struct {
     remoteWallet  *RemoteWallet    // Service location scanning
     url           *accounts.URL    // Textual URL uniquely identifying this wallet
     driver         driver          // driver that implements access to signing server

     accounts []accounts.Account                         // List of accounts found on signing server
     paths    map[common.Address]accounts.DerivationPath // Known derivation paths for signing operations

     healthQuit chan chan error

// Locking a hardware wallet is a bit special. Since hardware devices are lower
// performing, any communication with them might take a non negligible amount of
// time. Worse still, waiting for user confirmation can take arbitrarily long,
// but exclusive communication must be upheld during. Locking the entire wallet
// in the mean time however would stall any parts of the system that don't want
// to communicate, just read some state (e.g. list the accounts).
//
// As such, a hardware wallet needs two locks to function correctly. A state
// lock can be used to protect the wallet's software-side internal state, which
// must not be held exclusively during hardware communication. A communication
// lock can be used to achieve exclusive access to the device itself, this one
// however should allow "skipping" waiting for operations that might want to
// use the device, but can live without too (e.g. account self-derivation).
//
// Since we have two locks, it's important to know how to properly use them:
//   - Communication requires the `device` to not change, so obtaining the
//     commsLock should be done after having a stateLock.
//   - Communication must not disable read access to the wallet state, so it
//     must only ever hold a *read* lock to stateLock.
     commsLock chan struct{} // Mutex (buf=1) for the USB comms without keeping the state locked
     stateLock sync.RWMutex  // Protects read and write access to the wallet struct fields

     log log.Logger // Contextual logger to tag the base with its id
}

// URL implements accounts.Wallet, returning the URL of the USB hardware device.
func (w *wallet) URL() accounts.URL {
     return *w.url // Immutable, no need for a lock
}

// Status implements accounts.Wallet, returning a custom status message from the
// underlying vendor-specific hardware wallet implementation.
func (w *wallet) Status() (string, error) {
     w.log.Debug("wallet.Status")
     w.stateLock.RLock() // No device communication, state lock is enough
     defer w.stateLock.RUnlock()

     status, failure := w.driver.Status()
     return status, failure
}

// Open implements accounts.Wallet
func (w *wallet) Open(passphrase string) error {
     w.log.Debug("wallet.Open")
     w.stateLock.Lock() // State lock is enough since there's no connection yet at this point
     defer w.stateLock.Unlock()

     // If the device was already opened once, refuse to try again
     if w.paths != nil {
	return accounts.ErrWalletAlreadyOpen
     }
     // Delegate device initialization to the underlying driver
     if err := w.driver.Open(passphrase); err != nil {
		return err
     }
     // Connection successful, start life-cycle management
     w.paths = make(map[common.Address]accounts.DerivationPath)

     w.healthQuit = make(chan chan error)

     go w.heartbeat()

     // Notify anyone listening for wallet events that a new device is accessible
     go w.remoteWallet.updateFeed.Send(accounts.WalletEvent{Wallet: w, Kind: accounts.WalletOpened})

     return nil
}

// heartbeat is a health check loop for the remote wallets to periodically verify
// whether they are still present or if they malfunctioned.
func (w *wallet) heartbeat() {
	w.log.Debug("Remote Wallet health-check started")
	defer w.log.Debug("Remote Wallet health-check stopped")

	// Execute heartbeat checks until termination or error
	var (
		errc chan error
		err  error
	)
	for errc == nil && err == nil {
		// Wait until termination is requested or the heartbeat cycle arrives
		select {
		case errc = <-w.healthQuit:
			// Termination requested
			continue
		case <-time.After(heartbeatCycle):
			// Heartbeat time
		}
		// Execute a tiny data exchange to see responsiveness
		w.stateLock.RLock()
		<-w.commsLock // Don't lock state while resolving version
		err = w.driver.Heartbeat()
		w.commsLock <- struct{}{}
		w.stateLock.RUnlock()

		if err != nil {
			w.stateLock.Lock() // Lock state to tear the wallet down
			w.close()
			w.stateLock.Unlock()
		}
		// Ignore non hardware related errors
		err = nil
	}
	// In case of error, wait for termination
	if err != nil {
		w.log.Debug("Remote Wallet health-check failed", "err", err)
		errc = <-w.healthQuit
	}
	errc <- err
}

// Close implements accounts.Wallet, closing the USB connection to the device.
func (w *wallet) Close() error {
	// Ensure the wallet was opened
        w.log.Debug("wallet.Close")
	w.stateLock.RLock()
	hQuit := w.healthQuit
	w.stateLock.RUnlock()

	// Terminate the health checks
	var herr error
	if hQuit != nil {
		errc := make(chan error)
		hQuit <- errc
		herr = <-errc // Save for later, we *must* close the USB
	}
	// Terminate the device connection
	w.stateLock.Lock()
	defer w.stateLock.Unlock()

	w.healthQuit = nil

	if err := w.close(); err != nil {
		return err
	}
	if herr != nil {
		return herr
	}
	return nil
}

// close is the internal wallet closer that terminates the USB connection and
// resets all the fields to their defaults.
//
// Note, close assumes the state lock is held!
func (w *wallet) close() error {
	// Close the device, clear everything, then return

        w.log.Debug("wallet.close")
	w.accounts, w.paths = nil, nil
	w.driver.Close()

	return nil
}

// Accounts implements accounts.Wallet, returning the list of accounts pinned to
// the USB hardware wallet. If self-derivation was enabled, the account list is
// periodically expanded based on current chain state.
func (w *wallet) Accounts() []accounts.Account {
        var err error
	// Return whatever account list we ended up with
        w.log.Debug("wallet.Accounts")
 
	w.stateLock.RLock()
	defer w.stateLock.RUnlock()

        w.accounts, err = w.driver.ReadAccounts()
        if err != nil {
           w.log.Debug("wallet.Accounts", "err", err)
           return []accounts.Account{}
        }
	cpy := make([]accounts.Account, len(w.accounts))
	copy(cpy, w.accounts)
	return cpy
}


// Contains implements accounts.Wallet, returning whether a particular account is
// or is not pinned into this wallet instance. Although we could attempt to resolve
// unpinned accounts, that would be an non-negligible hardware operation.
func (w *wallet) Contains(account accounts.Account) bool {
        w.log.Debug("wallet.Contains")
	w.stateLock.RLock()
	defer w.stateLock.RUnlock()
        var  acctBytes []byte
        var  cmpBytes []byte

        acctBytes = account.Address.Bytes()

        for _, acct := range w.accounts {
            cmpBytes = acct.Address.Bytes()
            if bytes.Equal(acctBytes[:],cmpBytes[:]) {
               return true
            }
        }
        fmt.Println("Account not found ", hex.EncodeToString(account.Address.Bytes()))
        return false
}

// Derive implements accounts.Wallet, deriving a new account at the specific
// derivation path. If pin is set to true, the account will be added to the list
// of tracked accounts.
func (w *wallet) Derive(path accounts.DerivationPath, pin bool) (accounts.Account, error) {
     w.log.Debug("wallet.Derive %s", path)
     return accounts.Account{}, accounts.ErrNotSupported
}
func (w *wallet) SelfDerive(base accounts.DerivationPath, chain ethereum.ChainStateReader) {
     w.log.Debug("wallet.SelfDerive ", "base", base)
}



// SignHash implements accounts.Wallet, however signing arbitrary data is not
// supported for hardware wallets, so this method will always return an error.
func (w *wallet) SignHash(account accounts.Account, hash []byte) ([]byte, error) {
        w.log.Debug("wallet.SighHash")
	return nil, accounts.ErrNotSupported
}

//
// SignTx implements accounts.Wallet. It sends the transaction over to the signing
// server to sign the transaction.  The user must have unlocked their account
// through the web app for the transaction to be authorized  
//
func (w *wallet) SignTx(account accounts.Account, tx *types.Transaction, chainID *big.Int) (*types.Transaction, error) {

        w.log.Debug("wallet.SignTx")
	w.stateLock.RLock() // Comms have own mutex, this is for the state fields
	defer w.stateLock.RUnlock()

	// Make sure the requested account is contained within
        
        if w.Contains(account) == false {
	   return nil, accounts.ErrUnknownAccount
	}
	// Ask the driver to send the transaction to the signing server
	sender, signedTx, err := w.driver.SignTx(account, tx, chainID)
	if err != nil {
		return nil, err
	}
	if sender != account.Address {
	   return nil, fmt.Errorf("signer mismatch: expected %s, got %s", account.Address.Hex(), sender.Hex())
	}
	return signedTx, nil
}

// SignHashWithPassphrase implements accounts.Wallet, however signing arbitrary
// data is not supported for Ledger wallets, so this method will always return
// an error.
func (w *wallet) SignHashWithPassphrase(account accounts.Account, passphrase string, hash []byte) ([]byte, error) {
        w.log.Debug("wallet.SignHashWithPassphrase")
	return w.SignHash(account, hash)
}

// SignTxWithPassphrase implements accounts.Wallet, attempting to sign the given
// transaction with the given account using passphrase as extra authentication.
// Since USB wallets don't rely on passphrases, these are silently ignored.
func (w *wallet) SignTxWithPassphrase(account accounts.Account, passphrase string, tx *types.Transaction, chainID *big.Int) (*types.Transaction, error) {
        w.log.Debug("wallet.SignTxWithPassphrase")
	return w.SignTx(account, tx, chainID)
}
