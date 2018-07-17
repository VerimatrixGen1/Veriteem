pragma solidity ^0.4.15;

contract AccessRights {
  
  uint constant MAX_GUARDIANSHIP = 20;
  uint constant MAX_FUNC_LIST = 50;
  
  struct ContractStruct{
    string        Name;
    uint          Guardianship;
    address       NewAddress;
    bool          WriteValid;
    bool          GlobalReadValid;
    uint          State;
    uint [MAX_GUARDIANSHIP] SubGuardianshipList;
    address [MAX_FUNC_LIST]  FunctionList;
    uint    [MAX_FUNC_LIST]  AccessGroupList;
  }
  
  mapping (address => ContractStruct) ContractTable;
  
  struct GuardianshipStruct{
    string        Name;
    address [2]   GuardianList;
    address []    ContractList;
    address []    ContributorList;
    address       AddVote;
    address       RemoveVote;
  }
  
  GuardianshipStruct  [MAX_GUARDIANSHIP] GuardianshipTable;
  
  struct ContributorStruct{
    string  Name;
    uint    Guardianship;
    uint    Limit;
    uint    AccessGroup;
    uint    LastBlockNumber;
  }
  
  mapping (address => ContributorStruct) ContributorTable;
  
  function InitGuardianship() public
  {
    if (GuardianshipTable[1].GuardianList[0] == 0)
      GuardianshipTable[1].GuardianList[0] = msg.sender;
      
    return;
  }  
  
  function WriteContractFunctionIndex(address Contract, uint FunctionIndex, address FunctionAddress, uint AccessGroup) public
  {
    bool Match;
    uint Index;
    (Match, Index) = GuardianshipIndex(msg.sender);
    if (!Match)
      return;
      
    if (ContractTable[Contract].Guardianship != Index)
      return;
      
    ContractTable[Contract].FunctionList[FunctionIndex] = FunctionAddress;
    ContractTable[Contract].AccessGroupList[FunctionIndex] = AccessGroup;
  }
  
  function ReadContractFunctionIndex(address Contract, uint FunctionIndex) public constant returns (address FunctionAddress, uint AccessGroup)
  {
    FunctionAddress = ContractTable[Contract].FunctionList[FunctionIndex];
    AccessGroup     = ContractTable[Contract].AccessGroupList[FunctionIndex];
    return;
  }
  
  function ReadContractFunctionAccessGroup(address Contract, address FunctionAddress) public constant returns (bool Match, uint AccessGroup)
  {
    uint Loop;
    Match = false;
    AccessGroup = 0xFFFFFFFF;
    Loop = 0;
    while (Loop < MAX_FUNC_LIST)
    {
      if (ContractTable[Contract].FunctionList[Loop] == 0)
        return;
      if (ContractTable[Contract].FunctionList[Loop] == FunctionAddress)
      {
        AccessGroup = ContractTable[Contract].AccessGroupList[Loop];
        Match = true;
        return;
      }
      Loop = Loop + 1;
    }
  }
  
  function WriteGuardianshipName (string Name) public
  {
    bool Match;
    uint Index;
    (Match, Index) = GuardianshipIndex(msg.sender);
    if (!Match)
      return;
    GuardianshipTable[Index].Name = Name;    
  }
  
  function ReadGuardianshipContributor(address GuardianAddress, uint ListIndex) public constant returns (address RetContributorAddress)
  {
    bool Match;
    uint Index;
    
    (Match, Index) = GuardianshipIndex(GuardianAddress);
    if (!Match)
      return;

    RetContributorAddress = GuardianshipTable[Index].ContributorList[ListIndex];
    return;
  }
  
  function ReadGuardianshipContract(address GuardianAddress, uint ListIndex) public constant returns (address RetContractAddress)
  {
    bool Match;
    uint Index;
    
    (Match, Index) = GuardianshipIndex(GuardianAddress);
    if (!Match)
      return;
    RetContractAddress = GuardianshipTable[Index].ContractList[ListIndex];
    return;
  }
  
  function ReadGuardianship(address GuardianAddress) public constant returns (
                  bool Match, 
                  uint GIndex, 
                  address GuardianA, 
                  address GuardianB,
                  string Name, 
                  uint ContractListLength, 
                  uint ContributorListLength, 
                  address AddVote, 
                  address RemoveVote)
  {
    Name = "NULL";
    ContractListLength = 0;
    ContributorListLength = 0;
    AddVote = 0;
    RemoveVote = 0;
    
    uint Index;
      
    (Match, Index) = GuardianshipIndex(GuardianAddress);
    if (!Match)
      return;
      
    GIndex                = Index;
    GuardianA             = GuardianshipTable[Index].GuardianList[0];
    GuardianB             = GuardianshipTable[Index].GuardianList[1];
    Name                  = GuardianshipTable[Index].Name;
    ContractListLength    = GuardianshipTable[Index].ContractList.length;
    ContributorListLength = GuardianshipTable[Index].ContributorList.length;
    AddVote               = GuardianshipTable[Index].AddVote;
    RemoveVote            = GuardianshipTable[Index].RemoveVote;
    return;
  }

  function ReadGuardianshipIndex(uint Index) public constant returns (
                address GuardianA, 
                address GuardianB, 
                string Name, 
                uint ContractListLength, 
                uint ContributorListLength, 
                address AddVote, 
                address RemoveVote)
  {
    GuardianA             = GuardianshipTable[Index].GuardianList[0];
    GuardianB             = GuardianshipTable[Index].GuardianList[1];
    Name                  = GuardianshipTable[Index].Name;
    ContractListLength    = GuardianshipTable[Index].ContractList.length;
    ContributorListLength = GuardianshipTable[Index].ContributorList.length;
    AddVote               = GuardianshipTable[Index].AddVote;
    RemoveVote            = GuardianshipTable[Index].RemoveVote;
    return;
  }
  
  function WriteContractInfo(address ContractAddress, string Name, address NewAddress, bool WriteValid, bool GlobalReadValid, uint State) public
  {
    bool Match;
    uint Index;
    
    (Match, Index) = GuardianshipIndex(msg.sender);
    if (!Match)
      return;

    if (ContractTable[ContractAddress].Guardianship != Index)
      return;
    
    ContractTable[ContractAddress].Name           = Name;
    ContractTable[ContractAddress].NewAddress     = NewAddress;
    ContractTable[ContractAddress].WriteValid     = WriteValid;
    ContractTable[ContractAddress].GlobalReadValid = GlobalReadValid;
    ContractTable[ContractAddress].State          = State;
  }
  
  function WriteContractSubGuardianship(address ContractAddress, address SubGuardianId, uint Index) public
  {
    bool Match;
    uint GIndex;

    (Match, GIndex) = GuardianshipIndex(msg.sender);
    if (!Match)
      return;

    if (ContractTable[ContractAddress].Guardianship != GIndex)
      return;
      
    (Match, GIndex) = GuardianshipIndex(SubGuardianId);
    if (!Match)
      return;
      
    ContractTable[ContractAddress].SubGuardianshipList[Index] = GIndex;
    return;
  }
  
  function ReadContractSubGuardianship(address ContractAddress, uint Index) public constant returns (uint SubGuardianship)
  {
    SubGuardianship = ContractTable[ContractAddress].SubGuardianshipList[Index];
    return;
  }
  
  function ReadContractInfo(address ContractAddress) public constant returns (
                  uint Guardianship, 
                  string Name, 
                  address NewAddress, 
                  bool WriteValid, 
                  bool GlobalReadValid, 
                  uint State)
  {
    Guardianship  = ContractTable[ContractAddress].Guardianship;
    Name          = ContractTable[ContractAddress].Name;
    NewAddress    = ContractTable[ContractAddress].NewAddress;
    WriteValid    = ContractTable[ContractAddress].WriteValid;
    GlobalReadValid = ContractTable[ContractAddress].GlobalReadValid;
    State         = ContractTable[ContractAddress].State;
    return;
  }
  
  function GuardianshipIndex (address GuardianAddress) public constant returns (bool Match, uint Index)
  {

    Match = false;
    Index = 0;
    
    for (uint Loop = 1; Loop < MAX_GUARDIANSHIP; Loop ++)
    {
      // If the address is 0, then we are looking for an empty slot in which case both addresses
      // need to be empty
      if (GuardianAddress == 0)
      {
        if ((GuardianshipTable[Loop].GuardianList[0] == GuardianAddress) && (GuardianshipTable[Loop].GuardianList[1] == GuardianAddress))
        {
          Match = true;
          Index = Loop;
          return;
        }
      }
      else
      {
        if ((GuardianshipTable[Loop].GuardianList[0] == GuardianAddress) || (GuardianshipTable[Loop].GuardianList[1] == GuardianAddress))
        {
          Match = true;
          Index = Loop;
          return;
        }
      }
    }
    return;
  }
  
  function WriteGuardian(address NewGuardianAddress) public
  {
    bool Match;
    uint Index;
      
    (Match, Index) = GuardianshipIndex(msg.sender);
    if (!Match)
      return;
      
    if (GuardianshipTable[Index].GuardianList[0] == msg.sender)
      GuardianshipTable[Index].GuardianList[1]  = NewGuardianAddress;
      
    if (GuardianshipTable[Index].GuardianList[1] == msg.sender)
      GuardianshipTable[Index].GuardianList[0]  = NewGuardianAddress;
  }
  
  function CreateContract(address ContractAddress) public
  {
    bool Match;
    uint Index;
      
    (Match, Index) = GuardianshipIndex(msg.sender);
    if (!Match)
      return;

    // Exit if the Contract is already managed by another guardian
    if ((ContractTable[ContractAddress].Guardianship != 0) && (ContractTable[ContractAddress].Guardianship != Index))
      return;
    
    
    // Check if the Contract already exsist in the Guardian's Contrct list
    for (uint Loop = 0; Loop < GuardianshipTable[Index].ContractList.length; Loop ++)
    {
      if (GuardianshipTable[Index].ContractList[Loop] == ContractAddress)
        return;
    }
    
    // Add Contract to Gaurdian's User List
    GuardianshipTable[Index].ContractList.push(ContractAddress);
    
    // Init Contract Table
    ContractTable[ContractAddress].Guardianship = Index;
    ContractTable[ContractAddress].Name         = "";
    ContractTable[ContractAddress].NewAddress   = 0;
    ContractTable[ContractAddress].WriteValid   = true;
    ContractTable[ContractAddress].GlobalReadValid = true;
    ContractTable[ContractAddress].State        = 1;

    return;
  }
  
  function CreateContributor(address ContributorAddress, string Name, uint Limit, uint AccessGroup) public
  {
    bool Match;
    uint Index;
      
    (Match, Index) = GuardianshipIndex(msg.sender);
    if (!Match)
      return;

    // Exit if the user is already managed by another guardian
    if ((ContributorTable[ContributorAddress].Guardianship != 0) && (ContributorTable[ContributorAddress].Guardianship != Index))
      return;
    
    // Check if the user already exsist in the Guardian's user list
    for (uint Loop = 0; Loop < GuardianshipTable[Index].ContributorList.length; Loop ++)
    {
      if (GuardianshipTable[Index].ContributorList[Loop] == ContributorAddress)
        return;
    }
    
    // Add user to Gaurdian's User List
    GuardianshipTable[Index].ContributorList.push(ContributorAddress);
    
    // Init User Table
    ContributorTable[ContributorAddress].Name         = Name;
    ContributorTable[ContributorAddress].Limit        = Limit;
    ContributorTable[ContributorAddress].Guardianship = Index;
    ContributorTable[ContributorAddress].AccessGroup  = AccessGroup;
    return;
  }
  
  function WriteContributor(address ContributorAddress, string Name, uint Limit, uint AccessGroup) public
  {
    bool Match;
    uint Index;

    (Match, Index) = GuardianshipIndex(msg.sender);
    if (!Match)
      return;

    if (ContributorTable[ContributorAddress].Guardianship != Index)
      return;

    ContributorTable[ContributorAddress].Name           = Name;
    ContributorTable[ContributorAddress].Limit          = Limit;
    ContributorTable[ContributorAddress].LastBlockNumber = block.number;
    ContributorTable[ContributorAddress].AccessGroup    = AccessGroup;
    return;
  }
  
  function ReadContributor(address ContributorAddress) public constant returns (
            uint Guardianship, 
            string Name, 
            uint Limit, 
            uint LastBlockNumber, 
            uint AccessGroup)
  {
    Guardianship   = ContributorTable[ContributorAddress].Guardianship;
    Name           = ContributorTable[ContributorAddress].Name;
    Limit          = ContributorTable[ContributorAddress].Limit;
    LastBlockNumber = ContributorTable[ContributorAddress].LastBlockNumber;
    AccessGroup    = ContributorTable[ContributorAddress].AccessGroup;
    return;
  }
  
  function DeleteContributor(address ContributorAddress) public
  {
    bool Match;
    uint Index;
      
    (Match, Index) = GuardianshipIndex(msg.sender);
    if (!Match)
      return;

    if ((ContributorTable[ContributorAddress].Guardianship != 0) && (ContributorTable[ContributorAddress].Guardianship != Index))
      return;

    for (uint Loop = 0; Loop < GuardianshipTable[Index].ContributorList.length; Loop ++)
    {
      if (GuardianshipTable[Index].ContributorList[Loop] == ContributorAddress)
      {
        GuardianshipTable[Index].ContributorList[Loop]      = 0;
        ContributorTable[ContributorAddress].Name           = "";
        ContributorTable[ContributorAddress].Limit          = 0;
        ContributorTable[ContributorAddress].Guardianship   = 0;
        ContributorTable[ContributorAddress].LastBlockNumber = 0;
        ContributorTable[ContributorAddress].AccessGroup    = 0;

        return;
      }
    }
    return;
  }
  
  function VerifyContractSubGuardianshipList(address ContractId, uint Guardianship) public constant returns (bool Match)
  {
    Match = false;

    // If the Requested Guardianship is 0 then return invalid
    if (Guardianship == 0)
      return;
      
    // If the contract has no Guadian, then the subGuardianList is invalid
    if ((GuardianshipTable[ContractTable[ContractId].Guardianship].GuardianList[0] == 0) &&
      (GuardianshipTable[ContractTable[ContractId].Guardianship].GuardianList[1] == 0))
      return;
    
    if (ContractTable[ContractId].Guardianship == Guardianship)
    {
      Match = true;
      return;
    }
    
    for (uint Loop = 0; Loop < MAX_GUARDIANSHIP; Loop++)
    {
      if (ContractTable[ContractId].SubGuardianshipList[Loop] == Guardianship)
      {
        Match = true;
        return;
      }
    }
    
    return;
    
  }
  
  function VerifyContractAccess(address ContractId, address FunctionAddress) public constant returns (bool ReadApproved, bool WriteApproved)
  {
    bool  Match;
    uint  AccessGroup;
    
    ReadApproved = false;
    WriteApproved = false;
    
    // Block all access to unowned contracts
    if ((GuardianshipTable[ContractTable[ContractId].Guardianship].GuardianList[0] == 0) &&
      (GuardianshipTable[ContractTable[ContractId].Guardianship].GuardianList[1] == 0))
      return;

      
    (Match, AccessGroup) = ReadContractFunctionAccessGroup(ContractId, FunctionAddress);
    if (Match && ((AccessGroup & ContributorTable[msg.sender].AccessGroup) == 0))
      return;

    // If GlobalRead approved, then the guardian check is not needed
    ReadApproved = ContractTable[ContractId].GlobalReadValid;
    
    // If the user has the same guardian as the contract (or subguardian)
    // then ReadApproved = Contract.ReadValid
    // Then WriteApproved = Contract.WriteValid only if under the user limit      
    if (VerifyContractSubGuardianshipList(ContractId, ContributorTable[msg.sender].Guardianship))
    {
      if (ContractTable[ContractId].GlobalReadValid)
        ReadApproved = true;
      
      if (ContributorTable[msg.sender].Limit > 0)
      {
        // Verify that the user has not exceed their rate limit
        if ((ContributorTable[msg.sender].LastBlockNumber + ContributorTable[msg.sender].Limit) > block.number)
          WriteApproved = false;
        else
          WriteApproved = ContractTable[ContractId].WriteValid;
      }
      else
        WriteApproved = ContractTable[ContractId].WriteValid;
    }
    
    return;
    
  }
  
  function UpdateContributorBlock() public
  {
    ContributorTable[msg.sender].LastBlockNumber = block.number;
    return;
  }  
  
  function GuardianshipVoteStats(address NewGuardian) public constant returns (uint AddAgreeCount, uint AddDisagreeCount, uint RemoveAgreeCount, uint RemoveDisagreeCount)
  {
    uint Loop = 1;
    AddAgreeCount = 0;
    AddDisagreeCount = 0;
    RemoveAgreeCount = 0;
    RemoveDisagreeCount = 0;
    while (Loop < MAX_GUARDIANSHIP)
    {
      // Make sure the ContractAdmin is a valid ID when counting votes
      if ((GuardianshipTable[Loop].GuardianList[0] != 0) || (GuardianshipTable[Loop].GuardianList[1] != 0))
      {
        // Update Add
        if (GuardianshipTable[Loop].AddVote == NewGuardian)
          AddAgreeCount = AddAgreeCount + 1;
        else
          AddDisagreeCount = AddDisagreeCount + 1;
          
        // Update Remove
        if (GuardianshipTable[Loop].RemoveVote == NewGuardian)
          RemoveAgreeCount = RemoveAgreeCount + 1;
        else
          RemoveDisagreeCount = RemoveDisagreeCount + 1;
      }
        
      Loop = Loop + 1;
    }
    
    return;

  }
  
  function GuardianshipVote(address VoteId, bool AddVote) public
  {
    bool    Match;
    uint    Index;
    uint    Loop;
    uint    NewIndex;
    uint    AddAgreeCount;
    uint    AddDisagreeCount;
    uint    RemoveAgreeCount;
    uint    RemoveDisagreeCount;
    address ContractId;
    address ContributorId;
    
    // If Admin list is empty, then allow first write?
    (Match, Index) = GuardianshipIndex(msg.sender);
    
    if (!Match)
      return;
    
    if (AddVote)
      GuardianshipTable[Index].AddVote = VoteId;
    else
      GuardianshipTable[Index].RemoveVote = VoteId;
      
    // Return if the Guardian is only clearing their vote
    if (VoteId == 0)
      return;
      
    // Check if more than half agree on the new admin
    (AddAgreeCount, AddDisagreeCount, RemoveAgreeCount, RemoveDisagreeCount) = GuardianshipVoteStats(VoteId);
    
    // clear new admin list if majority vote in new admin
    if (((AddAgreeCount > AddDisagreeCount) && AddVote) || ((RemoveAgreeCount > RemoveDisagreeCount) && !AddVote))
    {
      // Find Blank index
      if (AddVote)
        (Match, NewIndex) = GuardianshipIndex(0);
      else
        (Match, NewIndex) = GuardianshipIndex(VoteId);
        
      if (Match)
      {
        if (AddVote)
        {
          // Add new Guardian
          GuardianshipTable[NewIndex].GuardianList[0] = VoteId;
          GuardianshipTable[NewIndex].GuardianList[1] = 0;
        }
        else
        {
          // Remove Guardian
          GuardianshipTable[NewIndex].GuardianList[0] = 0;
          GuardianshipTable[NewIndex].GuardianList[1] = 0;
          GuardianshipTable[NewIndex].Name            = "";
          GuardianshipTable[NewIndex].AddVote         = 0;
          GuardianshipTable[NewIndex].RemoveVote      = 0;
          
          // Disable all contracts
          for (Loop = 0; Loop < GuardianshipTable[NewIndex].ContractList.length; Loop++)
          {
            ContractId = GuardianshipTable[NewIndex].ContractList[Loop];
            ContractTable[ContractId].Name          = "";
            ContractTable[ContractId].Guardianship  = 0;
            ContractTable[ContractId].NewAddress    = 0;
            ContractTable[ContractId].WriteValid    = false;
            ContractTable[ContractId].GlobalReadValid = false;
            ContractTable[ContractId].State         = 0;
          }

          // Disable all Users
          for (Loop = 0; Loop < GuardianshipTable[NewIndex].ContributorList.length; Loop++)
          {
            ContributorId = GuardianshipTable[NewIndex].ContributorList[Loop];
            ContributorTable[ContributorId].Name            = "";
            ContributorTable[ContributorId].Guardianship    = 0;
            ContributorTable[ContributorId].Limit           = 0;
            ContributorTable[ContributorId].Guardianship    = 0;
            ContributorTable[ContributorId].AccessGroup     = 0;
            ContributorTable[ContributorId].LastBlockNumber = 0;
          }
        }
          
      }
    }
    return;

  }
}
    