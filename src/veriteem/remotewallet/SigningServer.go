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
	"io/ioutil"
	"fmt"
	"time"
	"errors"
	"bytes"
	"net/http"
	"encoding/json"

	"github.com/ethereum/go-ethereum/accounts"
	"github.com/ethereum/go-ethereum/common"
        "github.com/ethereum/go-ethereum/log"
)

type SigningServer struct {
     serverURL  string
     scheme     string
     log        log.Logger
     connected  bool 
     failed     bool 
     cache      serverCache      
}

// fileCache is a cache of files seen during scan of keystore.
type serverCache struct {
        all     []accounts.Account // all accounts read from the signing server
        lastMod time.Time          // Last time instance when an account was modified
}

type responseJSON struct {
     Status      string `json:"Status"`
     Accounts  []string `json:"Accounts"`
}

func (sc *SigningServer) ReadAccountsFromServer() ([]accounts.Account, error) {

     fmt.Println("SigningServer.ReadAccountsFromServer")
     if sc == nil {
        fmt.Print("signingServer.ReadAccountsFromServer: sc is null\n")
        return []accounts.Account{}, fmt.Errorf("sc is null ")
     }

     var netClient = &http.Client {
         Timeout: time.Second * 20,        
     }

     //
     // Request the account list from the signing server
     //
     request := fmt.Sprintf("%s/ListAccounts", sc.serverURL)  
     sc.log.Debug("ReadAccounts", "req", request)

     response, err := netClient.Get(request)
     if err != nil {
        sc.log.Debug("ReadAccounts", "err", err)
        return []accounts.Account{}, err
     }
     defer response.Body.Close()

     //
     // The reponse is json formatted data
     //
     buf, err := ioutil.ReadAll(response.Body)
     if err != nil {
        sc.log.Debug("ReadAccounts", "err", err)
        return []accounts.Account{}, err
     }
     var accountListJs  responseJSON
     json.Unmarshal(buf, &accountListJs)
     
     accountList := make([]accounts.Account, len(accountListJs.Accounts))

     //
     // Convert the json structure to a serverAccount array
     //
     var idx  int
     idx = 0
     for _, acct := range accountListJs.Accounts {
         acctH := common.HexToAddress(acct)
         var account accounts.Account
         account.Address    = acctH
         account.URL.Scheme = sc.scheme
         account.URL.Path   = sc.serverURL
         accountList[idx] = account
         idx = idx + 1 
     }
     return accountList, nil
}

func (sc *SigningServer) NewAccount(passPhrase string) (accounts.Account, error) {
        addr, error := sc.SigningServerRequest()
        if error == nil {
           var a accounts.Account
           return a, errors.New("Cannot create account")
        }
	a := &accounts.Account{Address: addr, URL: accounts.URL{Scheme: sc.scheme, Path: addr.Hex()}}
        return *a, nil
}

func (sc *SigningServer) SignTx(tx []byte) ([]byte, error) {
     url := fmt.Sprintf("%s/SignTx", sc.serverURL)  
     
     req, err := http.NewRequest("POST", url, bytes.NewBuffer(tx))
     req.Header.Set("X-Custom-Header", "signingserver")
     req.Header.Set("Content-Type", "application/json")

     client := &http.Client{}
     resp, err := client.Do(req)
     if err != nil {
         return nil, err
     }
     defer resp.Body.Close()

     body, _ := ioutil.ReadAll(resp.Body)
     
     return body, nil
}

func (sc *SigningServer) SigningServerRequest() (common.Address, error) {
     var addr common.Address
     return addr, nil
}
