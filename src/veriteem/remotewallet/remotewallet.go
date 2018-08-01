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

package remotewallet

import (
	"sync"
	"time"
	"fmt"

	"github.com/ethereum/go-ethereum/accounts"
	"github.com/ethereum/go-ethereum/event"
	"github.com/ethereum/go-ethereum/log"
 
)

// URL of signing server
const VeriteemSigningServer = "http://13.59.10.65:80"

// RemoteWalletScheme is the protocol scheme prefixing account and wallet URLs.
const RemoteWalletScheme = "remotewallet"


// refreshCycle is the maximum time between wallet refreshes 
const refreshCycle = 60 * time.Second

// refreshThrottling is the minimum time between wallet refreshes 
const refreshThrottling = 500 * time.Millisecond

// RemoteWallet is a accounts.Backend that can find and handle generic USB hardware wallets.
type RemoteWallet struct {
	signingServer SigningServer           // signing server that supports signing transactions
	scheme        string                  // Protocol scheme prefixing account and wallet URLs.
	makeDriver    func(SigningServer) driver // Factory method to construct a vendor specific driver

	refreshed     time.Time               // Time instance when the list of wallets was last refreshed
	wallets       []accounts.Wallet       // List of wallet servers currently tracking
	updateFeed    event.Feed              // Event feed to notify wallet additions/removals
	updateScope   event.SubscriptionScope // Subscription scope tracking current live listeners
	updating      bool                    // Whether the event notification loop is running

        log           log.Logger              // Contextual logger
	quit chan chan error

	stateLock sync.RWMutex // Protects the internals of the RemoteWallet from racey access

}

// NewVeriteemWallet creates a new hardware wallet manager for Ledger devices.
func NewVeriteemWallet() (*RemoteWallet, error) {
        
        log := log.New("SigningServer", VeriteemSigningServer)
        fmt.Printf("NewVeriteemWallet log %v\n", log)
        signingServer := SigningServer {
                          serverURL: VeriteemSigningServer,
                          scheme:    RemoteWalletScheme,
                          log:       log,
                          connected: false,
                          failed:    false,
        }
        fmt.Printf("SigningServer %v\n", signingServer)
	return newRemoteWallet(RemoteWalletScheme, signingServer, newVeriteemDriver)
}

// newRemoteWallet creates a new hardware wallet manager for generic USB devices.
func newRemoteWallet(scheme string, server SigningServer, makeDriver func(SigningServer) driver) (*RemoteWallet, error) {
	remoteWallet := &RemoteWallet{
		scheme:        scheme,
		signingServer: server,
		makeDriver:    makeDriver,
		quit:          make(chan chan error),
                log:           server.log,
	}
        fmt.Printf("RemoteWallet %v\n", remoteWallet)
	remoteWallet.refreshWallets()
	return remoteWallet, nil
}

// Wallets implements accounts.Backend, returning all the currently tracked USB
// devices that appear to be hardware wallets.
func (remoteWallet *RemoteWallet) Wallets() []accounts.Wallet {
	// Make sure the list of wallets is up to date
        remoteWallet.log.Debug("remoteWallet.Wallets()")
	remoteWallet.refreshWallets()

	remoteWallet.stateLock.RLock()
	defer remoteWallet.stateLock.RUnlock()

	cpy := make([]accounts.Wallet, len(remoteWallet.wallets))
	copy(cpy, remoteWallet.wallets)
	return cpy
}

//
// refreshWallets creates the wallet instance if none exists and 
// sends and event of the wallet availability.  This implementation 
// supports a single wallet in the signing server
//

func (remoteWallet *RemoteWallet) refreshWallets() {
	// Don't scan the USB like crazy it the user fetches wallets in a loop

	elapsed := time.Since(remoteWallet.refreshed)
	if elapsed < refreshThrottling {
	   return
	}
	
	events := []accounts.WalletEvent{}

        //
        // If we have not created the wallet, create it now
        //
        if len(remoteWallet.wallets) == 0 {
	   wallets := make([]accounts.Wallet, 0, 1)
           url := accounts.URL{Scheme: remoteWallet.scheme, Path: VeriteemSigningServer}
           logger := log.New("wallet", remoteWallet.scheme)
           wallet := &wallet{remoteWallet: remoteWallet, driver: remoteWallet.makeDriver(remoteWallet.signingServer), url: &url, log: logger}
           wallets = append(wallets, wallet)
           events  = append(events, accounts.WalletEvent{Wallet: wallet, Kind: accounts.WalletArrived})
	   remoteWallet.wallets = wallets
        }
	remoteWallet.refreshed = time.Now()

	// Fire all wallet events and return
	for _, event := range events {
	    remoteWallet.updateFeed.Send(event)
	}
}

// Subscribe implements accounts.Backend, creating an async subscription to
// receive notifications on the addition or removal of USB wallets.
func (remoteWallet *RemoteWallet) Subscribe(sink chan<- accounts.WalletEvent) event.Subscription {
	// We need the mutex to reliably start/stop the update loop
	remoteWallet.stateLock.Lock()
	defer remoteWallet.stateLock.Unlock()

        remoteWallet.log.Debug("remoteWallet.Subscribe()")

	// Subscribe the caller and track the subscriber count
	sub := remoteWallet.updateScope.Track(remoteWallet.updateFeed.Subscribe(sink))

	// Subscribers require an active notification loop, start it
	if !remoteWallet.updating {
		remoteWallet.updating = true
		go remoteWallet.updater()
	}
	return sub
}

// updater is responsible for maintaining an up-to-date list of wallets managed
// by the signing server , and for firing wallet addition/removal events.
func (remoteWallet *RemoteWallet) updater() {
        remoteWallet.log.Debug("remoteWallet.Updater()")
	for {
		// TODO: Wait for a USB hotplug event (not supported yet) or a refresh timeout
		// <-hub.changes
		time.Sleep(refreshCycle)

		// Run the wallet refresher
		remoteWallet.refreshWallets()

		// If all our subscribers left, stop the updater
		remoteWallet.stateLock.Lock()
		if remoteWallet.updateScope.Count() == 0 {
			remoteWallet.updating = false
			remoteWallet.stateLock.Unlock()
			return
		}
		remoteWallet.stateLock.Unlock()
	}
}
