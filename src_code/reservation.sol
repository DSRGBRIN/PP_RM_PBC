// SPDX-License-Identifier: GPL-3.0
pragma solidity >=0.7;

contract Reservation{
    string public Name;
    address public Owner;
    uint64 public KCtr;                         //counter to keep track of updates
    struct _Pubkey{
        uint256 time;
        string key; 
    }
    mapping (uint => _Pubkey) public VPKey; 

    mapping (uint => string) public RT;  // index: table, index=yymmdd, table=_table

    mapping (address => bool) public isUser;    //boolean to record user  
    
    modifier onlyOwner() {
        require(msg.sender == Owner, "Not authorized");
        _;
    }
    modifier onlyUser() {
        require(isUser[msg.sender] == true, "Not authorized");
        _;
    }

    uint public reqCtr;                          //counter to keep track of updates 
    struct _Rsv{
        uint Fprm;
        string VID;
        string RR;
        string CP;
        string reply;
        uint8 state;
    }
    mapping (uint => _Rsv) public request;

    constructor(string memory _name, string memory _VPKey) {
        Owner = msg.sender;
        Name = _name; 
        VPKey[KCtr+1].key  = _VPKey;
        VPKey[KCtr+1].time = block.timestamp;
        KCtr += 1;
    }

    function Request(uint _Fprm, string memory _VID, string memory _RR, string memory _CP) public onlyUser {
        request[reqCtr+1].Fprm = _Fprm;
        request[reqCtr+1].VID = _VID;
        request[reqCtr+1].RR = _RR;
        request[reqCtr+1].CP = _CP;
        request[reqCtr+1].state = 1;
        reqCtr +=1;
    }

    function Reply(uint _reqID, bool _approved, string memory _UTT) public onlyOwner {
        require (request[_reqID].state == 1);
        if(_approved){  // replace RTT
            RT[request[_reqID].Fprm] = request[_reqID].CP; 
            request[_reqID].state = 2;
        }else{
            request[_reqID].state = 3;
        }
        request[_reqID].reply = _UTT;
    }

    function UpdateKey(string memory _VPkey) public onlyOwner {
        VPKey[KCtr+1].key = _VPkey;
        VPKey[KCtr+1].time = block.timestamp;
        KCtr +=1;
    }
    function addUser(address _user) public onlyOwner {
        require (isUser[_user] == false);
        isUser[_user] = true;
    }

    function getPKey()  public view returns (string memory _PKey) {
        _PKey = VPKey[KCtr].key;
    }
}
