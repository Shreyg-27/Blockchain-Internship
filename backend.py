
import hashlib
from time import time
from urllib.parse import urlparse
import requests
import json
from uuid import uuid4

class Blockchain:
    
    # Initialization of PARAMETERS
    def __init__(self):
        # one for storing transactions and 
        # the other for storing chain of blocks
        self.current_transactions = []
        #This initializes an empty list (self.current_transactions) to store transactions.
        # This list will be used to temporarily store transactions before they are added to a block.
        self.chain = []
        # This initializes an empty list (self.chain) to store the chain of blocks. Each block contains a list of
        # transactions, creating a chain of blocks that represents the entire transaction history.
        self.nodes = set()
        #This initializes an empty set (self.nodes) to store the network nodes. The set will be used to keep track of
        # other nodes in the blockchain network.
        # Creation of genesis block
        self.new_block(previous_hash=1, proof=100)
        # The line `self.new_block(previous_hash=1, proof=100)` in the `__init__` method initializes the blockchain
        # by creating the genesis block. The values `previous_hash=1` indicate that the genesis block has no predecessor,
        # and `proof=100` is an arbitrary placeholder for the proof of work associated with the genesis block.



        
    def register_node(self, address):
        # Adds new NODE to the LIST OF NODES
        parsed_url = urlparse(address)
        #The urlparse function is used to break down a URL into its components (scheme, netloc, path, etc.).
        # For example, if address is a URL like "http://example.com", parsed_url would be a named tuple with attributes
        # like scheme='http', netloc='example.com', path='', etc.
        self.nodes.add(parsed_url.netloc)
        #parsed_url.netloc extracts the network location part of the URL, which usually represents the domain name or
        # IP address and possibly the port number.
        #The add method is used to add the extracted network location (netloc) to the set of nodes (self.nodes)
        # in the blockchain.




    def valid_chain(self, chain):
        # Determine whether given BLOCKCHAIN is valid
        # last_block = chain[0]: Initializes the last_block variable with the first block (genesis block) of the given
        # blockchain chain. Current_index = 1: Initializes the current_index variable to 1 to start iterating
        last_block = chain[0]
        current_index = 1
        # Initiates a loop to iterate through all blocks in the given blockchain.
        while current_index < len(chain):
            #Prints the information of the current and last blocks for debugging purposes.
            block = chain[current_index]
            print(f'{last_block}')
            print(f'{block}')
            print("\n-----------\n")
            # Check whether HASH of the block is correct.
            # Checks whether the hash of the previous block (last_block) matches the previous_hash value in the
            # current block (block). If not, the chain is considered invalid, and the function returns False.
            if block['previous_hash'] != self.hash(last_block):
                return False
            # Calls the valid_proof method to check if the proof of work for the current block is valid.
            # If not, the function returns False.
            if not self.valid_proof(last_block['proof'], block['proof'],self.hash(last_block)):
                return False
        #  Updates the last_block variable for the next iteration. Current_index += 1: Increments the
        #  current_index for the next iteration.
        last_block = block
        current_index += 1
        return True




    # implementation of a consensus algorithm. It attempts to achieve consensus among nodes in a blockchain network by
    # comparing the lengths and validity of different chains held by nodes.
    def resolve_conflicts(self):
        # CONSENSUS algorithm
        # Initializes the neighbours variable with the set of nodes in the blockchain network.
        neighbours = self.nodes
        new_chain = None
        max_length = len(self.chain)
        # iterates through each node in the network to gather information about their chains and reach a consensus.
        for node in neighbours:
            # node stands for different centers of voting i.e, Polling centers
            # Polling centers are nothing but voter's vote input system
            # Sends a GET request to each node's /chain endpoint to retrieve information about their blockchain.
            response = requests.get(f'http://{node}/chain')
            #  Checks if the request was successful (status code 200).
            if response.status_code == 200:
                length = response.json()['length'] # Retrieves the length of the chain from the response.
                chain = response.json()['chain'] # Retrieves the chain itself from the response.
                # Checks if the length of the received chain is greater than the current maximum length (max_length)
                # and if the chain is valid according to the valid_chain method.
                if length > max_length and self.valid_chain(chain):
                    # If the received chain meets the consensus criteria, it becomes the new preferred chain.
                    # max_length = length: Updates the maximum length.
                    # new_chain = chain: Updates the new preferred chain.
                    max_length = length
                    new_chain = chain
        # Checks if a new preferred chain has been identified.
        # # self.chain = new_chain: Updates the blockchain with the new preferred chain.
        # # return True: Returns True to indicate that the blockchain was updated.
        if new_chain:
            self.chain = new_chain
            return True
        # No consensus reached
        return False




    def new_block(self, proof, previous_hash=None):
        # Creates NEW BLOCK in chain
        # uuid is the Universal Unique Identifier, generated randomly
        # which is a session key, vary from each session of poll. 
        # This is generated just before appending vote block into chain
        # Generates a unique identifier using the uuid4 function. This identifier is used as a session key and is
        # unique for each session of the poll.
        node_identifier = str(uuid4()).replace('-', '')
        block = {  # Creates a dictionary representing the new block with the following key-value pairs:
            'index': len(self.chain) + 1, # The index of the block in the blockchain (one more than the index of the last block).
            # Creates a dictionary representing the new block with the following key-value pairs:
            # This method returns the time as a floating point number 
            # expressed in seconds since the epoch January 1, 1970
            'timestamp': time(), # The current time when the block is created.
            'transactions': self.current_transactions, # The list of transactions in the block (cleared from current_transactions).
            'proof': proof, # The proof of work associated with the block.
            'session_key': node_identifier, # The unique identifier for the session.
            'previous_hash': previous_hash or self.hash(self.chain[-1]), # The hash of the previous block in the chain.
            # If previous_hash is not provided, it defaults to the hash of the last block in the existing chain.
            }
        self.current_transactions = [] # Clears the list of current transactions, as they are now included in the new block.
        self.chain.append(block) #  Adds the newly created block to the chain.
        return block # Returns the newly created block.



    # responsible for creating a new transaction and adding it to the list of current transactions.
    def new_transaction(self, Party_A , Party_B):
        # Appends a new transaction to the list of current transactions
        # The transaction is represented as a dictionary with the following key-value pairs:
        self.current_transactions.append({
            # Part_A is the nominee participating in the elections
            # Party_B is the voter who votes
            'Party_A': Party_A, #  Represents the nominee (party or candidate) participating in the elections.
            'Party_B': Party_B, # Represents the voter who is casting the vote.
            'Votes': 1 # Represents the number of votes, initialized to 1.
            })
        # Returns the index of the last block in the blockchain (self.last_block['index']) plus 1.
        # This indicates the index at which the new block incorporating the transaction will be added.
        return self.last_block['index'] + 1
    # the new_transaction method adds a new transaction to the list of current transactions, representing a
    # vote cast by a voter (Party_B) for a particular nominee or party (Party_A).
    # The method returns the index at which this transaction will be included in the next
    # block when the block is mined.




    @property  # decorator is used to define a getter method for a class attribute
    # defines a property called last_block in the Blockchain class.
    # The purpose of this property is to provide a convenient way to access the last block in the blockchain
    # The last_block property returns the last block in the blockchain, which is obtained by indexing self.chain[-1].
    # This syntax retrieves the last element of the self.chain list, which is the most recent block in the blockchain.
    # @property decorator in this context allows you to access the last block as if it were an attribute
    # rather than a method call. It enhances the readability of the code and makes it more intuitive to retrieve
    # information about the last block in the blockchain.
    def last_block(self):
        return self.chain[-1]



    
    @staticmethod  # Static methods are bound to the class rather than an instance of the class and don't have
    # access to the instance itself (self).
    def hash(block):
        # SHA-256, HASH of a Block
        block_string = json.dumps(block, sort_keys=True).encode()
        # Converts the given block (which is a dictionary representing a block) into a JSON-formatted string.
        # The sort_keys=True ensures that the keys in the JSON string are sorted for consistency.

        # Computes the SHA-256 hash of the UTF-8 encoded block_string and returns the hexadecimal representation of the hash.
        return hashlib.sha256(block_string).hexdigest()
    # this static method hash takes a block as input, converts it to a JSON-formatted string, and then
    # computes the SHA-256 hash of that string. It is used to generate a unique hash for a given block
    # in the blockchain. The @staticmethod decorator indicates that this method doesn't depend on the
    # state of a specific instance of the class and can be called on the class itself.



    #  responsible for finding a valid proof of work for a new block.
    #  It involves repeatedly incrementing a value (proof) until a specific condition is met.
    def proof_of_work(self, last_proof):
        # PROOF OF WORK
        proof = 0 # Initializes the variable proof to 0.

        #  Initiates a loop that continues until a valid proof of work is found.
        # The condition checks if the result of calling the valid_proof method with the current last_proof and
        # proof values is False.
        while self.valid_proof(last_proof, proof) is False:
            proof += 1 # Increments the proof value in each iteration of the loop.
        return proof
    # method is used to iteratively search for a valid proof of work by incrementing the proof value until
    # the condition specified by the valid_proof method is satisfied


    # used to check whether a given proof of work is valid. It involves creating a guess by combining
    # the previous proof and the current proof and checking if the hash of this guess satisfies a certain condition
    @staticmethod
    def valid_proof(last_proof, proof):
        guess = f'{last_proof}{proof}'.encode() # used to check whether a given proof of work is valid.
        # It involves creating a guess by combining the previous proof and the current proof and checking
        # if the hash of this guess satisfies a certain condition
        guess_hash = hashlib.sha256(guess).hexdigest() # Computes the SHA-256 hash of the guess and obtains the
        # hexadecimal representation of the hash.
        return guess_hash[:4] == "0000" # Checks if the first four characters of the hash are equal to "0000".
        # This condition is a common criterion for a valid proof of work in many blockchain implementations.
        # The number of leading zeros can be adjusted to control the difficulty of the proof of work


    # method determines the validity of a proof of work by concatenating the previous proof and the current proof,
    # hashing the result, and checking if the hash meets a certain criterion (in this case, having four leading zeros).
    # This method is often used in conjunction with the proof_of_work method to find a valid proof for a new block in
    # the blockchain.
