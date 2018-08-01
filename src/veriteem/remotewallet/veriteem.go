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

// This file contains the implementation for interacting with the Ledger hardware
// wallets. The wire protocol spec can be found in the Ledger Blue GitHub repo:
// https://raw.githubusercontent.com/LedgerHQ/blue-app-eth/master/doc/ethapp.asc

package remotewallet

import (
	"errors"
	"fmt"
	"math/big"
	"encoding/json"
	"encoding/hex"

	"github.com/ethereum/go-ethereum/accounts"
	"github.com/ethereum/go-ethereum/common"
	"github.com/ethereum/go-ethereum/core/types"
)

// ledgerOpcode is an enumeration encoding the supported Ledger opcodes.
type ledgerOpcode byte

// ledgerParam1 is an enumeration encoding the supported Ledger parameters for
// specific opcodes. The same parameter values may be reused between opcodes.
type ledgerParam1 byte

// ledgerParam2 is an enumeration encoding the supported Ledger parameters for
// specific opcodes. The same parameter values may be reused between opcodes.
type ledgerParam2 byte

// errLedgerReplyInvalidHeader is the error message returned by a Ledger data exchange
// if the device replies with a mismatching header. 
// 
var errLedgerReplyInvalidHeader = errors.New("ledger: invalid reply header")

// errLedgerInvalidVersionReply is the error message returned by a Ledger version retrieval
// when a response does arrive, but it does not contain the expected data.
var errLedgerInvalidVersionReply = errors.New("ledger: invalid version reply")

// VeriteemDriver implements the communication with the signing server for the wallet.
type VeriteemDriver struct {
	signingServer  SigningServer   // web address for signing services
	version        [3]byte         // Current version of the signing server (zero if app is offline)
	failure        error           // Any failure that would make the device unusable
}

type JsonTx struct {
     Account   string   `json:"account"`
     To        string   `json:"to"`
     Data      string   `json:"data"`
     Nonce     uint64   `json:"nonce"`
     GasLimit  uint64   `json:"gas"`
     Value     *big.Int `json:"value"`
     GasPrice  *big.Int `json:"gasPrice"`
     ChainId   *big.Int `json:"chainId"`
     
} 
type JsonRx struct {
     R        string  `json:"r"`
     S        string  `json:"s"`
     V        string  `json:"v"`
     Hash     string  `json:"hash"`
} 

type JsonSign struct {
     R         string   `json:"r"`
     S         string   `json:"s"`
     V         string   `json:"v"`
     To        string   `json:"to"`
     Nonce     string   `json:"nonce"`
     GasLimit  string   `json:"gas"`
     Value     string   `json:"value"`
     GasPrice  string   `json:"gasPrice"`
     ChainId   string   `json:"chainId"`
     Data      string   `json:"input"`
     Hash      string   `json:"hash"`
} 

// newVeriteemDriver creates a new instance of a veriteem protocol driver.
func newVeriteemDriver(signingServer SigningServer ) driver {
	return &VeriteemDriver{
                signingServer: signingServer,
	}
}

// Status implements usbwallet.driver, returning various states the Ledger can
// currently be in.
func (w *VeriteemDriver) Status() (string, error) {
	if w.failure != nil {
	   return fmt.Sprintf("Failed: %v", w.failure), w.failure
	}
	return fmt.Sprintf("Ethereum app v%d.%d.%d online", w.version[0], w.version[1], w.version[2]), w.failure
}

// offline returns whether the wallet and the Ethereum app is offline or not.
//
// The method assumes that the state lock is held!
func (w *VeriteemDriver) offline() bool {
	return w.version == [3]byte{0, 0, 0}
}

// Open implements usbwallet.driver, attempting to initialize the connection to the
// Ledger hardware wallet. The Ledger does not require a user passphrase, so that
// parameter is silently discarded.
func (w *VeriteemDriver) Open(passphrase string) error {

	// Try to resolve the Ethereum app's version, will fail prior to v1.0.2
	version, err := w.ledgerVersion() 
        if err != nil {
	   w.version = [3]byte{0, 0, 0} // Assume worst case, can't verify if v1.0.0 or v1.0.1
           return err
	}
        w.version = version
        return nil
}

// Close implements usbwallet.driver, cleaning up and metadata maintained within
// the Ledger driver.
func (w *VeriteemDriver) Close() error {
	w.version = [3]byte{}
	return nil
}

// Heartbeat implements usbwallet.driver, performing a sanity check against the
// Ledger to see if it's still online.
func (w *VeriteemDriver) Heartbeat() error {
	if _, err := w.ledgerVersion(); err != nil && err != errLedgerInvalidVersionReply {
		w.failure = err
		return err
	}
	return nil
}

// Derive implements usbwallet.driver, sending a derivation request to the Ledger
// and returning the Ethereum address located on that derivation path.
func (w *VeriteemDriver) Derive(path accounts.DerivationPath) (common.Address, error) {
     return common.Address{}, accounts.ErrNotSupported
}

// SignTx implements usbwallet.driver, sending the transaction to the Ledger and
// waiting for the user to confirm or deny the transaction.
//
// Note, if the version of the Ethereum application running on the Ledger wallet is
// too old to sign EIP-155 transactions, but such is requested nonetheless, an error
// will be returned opposed to silently signing in Homestead mode.
func (w *VeriteemDriver) SignTx(account accounts.Account, tx *types.Transaction, chainID *big.Int) (common.Address, *types.Transaction, error) {
        //
        // Send the transaction to the signing server for signing
        //
        var (
               JsonMsg   JsonTx
        )

        //
        //  Convert the transaction and account into a json payload 
        //

        JsonMsg.Account   = "0x" + hex.EncodeToString(account.Address.Bytes())
        JsonMsg.Data      = "0x" + hex.EncodeToString(tx.Data())
        JsonMsg.To        = tx.To().Hex()
        JsonMsg.GasPrice  = tx.GasPrice()
        JsonMsg.GasLimit  = tx.Gas()
        JsonMsg.Value     = tx.Value()
        JsonMsg.Nonce     = tx.Nonce()
        JsonMsg.ChainId   = chainID

        jsonPayload, errj   := json.Marshal(JsonMsg)
        if errj != nil {
           fmt.Println("Error umarshalling JsonMsg")
	   return common.Address{}, nil, errj
        } 

        //
        // Request the signing server to sign the transaction
        //
        jsonResponse, errj := w.signingServer.SignTx(jsonPayload)
        if errj != nil {
           fmt.Println("Signing Server returns error")
	   return common.Address{}, nil, errj
        }
        
        //
	// Unpack the signed transaction (R,S,V values) into this transaction
        //
        var jsonrx JsonRx
        errj = json.Unmarshal(jsonResponse, &jsonrx)
        if errj != nil {
           fmt.Println("Error unmarshall jsonResponse to jsonrx")
           fmt.Println("Error %s ", errj)
	   return common.Address{}, nil, errj
        }

        fmt.Println("jsonrx.S %s", jsonrx.S)
        fmt.Println("jsonrx.R %s", jsonrx.R)
        fmt.Println("jsonrx.V %s", jsonrx.V)

        var jsonTran JsonSign

        jsonTran.R        = jsonrx.R
        jsonTran.S        = jsonrx.S
        jsonTran.V        = jsonrx.V
        jsonTran.To       = JsonMsg.To
        jsonTran.Nonce    = fmt.Sprintf("0x%x", tx.Nonce())
        jsonTran.GasLimit = fmt.Sprintf("0x%x", tx.Gas())
        jsonTran.GasPrice = fmt.Sprintf("0x%x", tx.GasPrice())
        jsonTran.Value    = fmt.Sprintf("0x%x", tx.Value())
        jsonTran.ChainId  = chainID.String()
        jsonTran.Data     = "0x" + hex.EncodeToString(tx.Data())
        jsonTran.Hash     = jsonrx.Hash

        jsonbyte, errj   := json.Marshal(jsonTran)
        err := tx.UnmarshalJSON(jsonbyte)
        if err != nil {
           fmt.Println("tx.UnmarshalJSON %s", err)
           return common.Address{}, nil, err
        }
        fmt.Println("Returning tx ") 
        return account.Address, tx, nil
}
     
func (w *VeriteemDriver) ReadAccounts() ([]accounts.Account, error) {

     fmt.Println("Veriteem Reading Accounts")
     acct, err := w.signingServer.ReadAccountsFromServer()
     return acct, err
}

//
// ledgerVersion retrieves the current version of the Ethereum wallet app running
// on the signing server
//
func (w *VeriteemDriver) ledgerVersion() ([3]byte, error) {
	// Cache the version for future reference
	var version = [3]byte{1, 0, 0} 

        //
        // Send a request to the signing server to get the version
        //
	return version, nil
}

