
from flask import Flask, jsonify, request, render_template, redirect, url_for
from backend import Blockchain
import json

#Web App named app
app = Flask(__name__)

# Initializing class here
blockchain = Blockchain() #  Creates an instance of the Blockchain class, initializing the blockchain with a genesis block.

# Registered Voters with unique Identity
# Lists are created to store registered voter IDs (voterID_array), IDs for reference
# (vote_see_chain, vote_check), and miner IDs (minerID_array).
voterID_array=[
        'VOID001','VOID002','VOID003',
        'VOID004','VOID005','VOID006',
        'VOID007','VOID008','VOID009',
        'VOID010','VOID011','VOID012',
        'VOID013','VOID014','VOID015']
# For Reference
vote_see_chain=voterID_array.copy()
vote_check=voterID_array.copy()
minerID_array=[
    'MOID001','MOID002','MOID003']


# Displays a form for miners to enter their IDs.
# If a miner submits the form to mine, it redirects to the /mine/ endpoint.
# If a miner submits the form to vote, it redirects to the /initial/ endpoint.
# If a miner with a miner ID tries to vote, it displays a message that miners cannot vote.
@app.route('/',methods=['GET','POST'])
def start():
    # Miners Home Page
    if request.method=='POST':
        user=request.form["minerID"]
        if user in minerID_array and request.form['submit']=='mine':
            return redirect(url_for('mine'))
        if request.form['submit']=='vote':
            return redirect(url_for('initial'))
        if user in minerID_array and request.form['submit']=='vote':
            return '<h3>A miner with Miner ID cannot vote</h3>'
        else:
            return redirect(url_for("control",User="Miner",ID=user))
    else:
        return render_template('index.html')

# For Better User Interface
# Displays a form for voters to enter their IDs.
# If a voter submits the form to see the chain, it redirects to the /full_chain/ endpoint.
# If a voter submits the form to cast a new vote, it redirects to the /put_vote/<name> endpoint.
@app.route('/voter',methods=['POST','GET'])
def initial():
    # Voters Home Page
    if request.method=='POST':
        user=request.form["voterID"]
        if user in vote_see_chain and request.form["submit"]=='see_chain':
            return redirect(url_for('full_chain'))
        if user in voterID_array and request.form["submit"]=='new_vote':
            return redirect(url_for("put_vote",name=user))
        else:
            return redirect(url_for("control",User="Voter",ID=user))
    else:
        return render_template('initial.html')

# enders a template with a message indicating whether a user (voter/miner) with a given ID has already voted or does not exist.
@app.route('/<User>_repeat/<ID>')
def control(User,ID):
    # CONTROL Reload and Back Reference After Vote
    return render_template("repeat.html",User=User,ID=ID)


# Allows voters to cast a vote.
# Checks if the voter ID is in the voterID_array.
# If yes, removes the voter ID from the array and redirects to the /new_transaction/<name>/<option> endpoint.
# If no, renders the fillup.html template.
@app.route('/put_vote/<name>',methods=['POST','GET'])
def put_vote(name):
    # POLL vote by Voter
    if request.method=='POST'and name in voterID_array:
        voterID_array.remove(name)
        option=request.form['vote']
        return redirect(url_for("new_transaction",name=name,option=option))
    else:
        return render_template("fillup.html")

# The process of Mining
# This takes up the transactions done recently 
# and put all into a block and append to the chain
# Retrieves the last block from the blockchain.
# Gets the last proof from the last block.
# Uses the proof of work algorithm to find a new proof.
# Creates a new block with the new proof and appends it to the blockchain.
# Returns information about the mined block in JSON format.
@app.route('/mine/', methods=['GET'])
def mine():
    last_block = blockchain.last_block
    last_proof = last_block['proof']
    proof = blockchain.proof_of_work(last_proof)
    
    block = blockchain.new_block(proof)
    data = {
        'message': "New Block Mined",
        'index': block['index'],
        'transactions': block['transactions'],
        'proof': block['proof'],
        'previous_hash': block['previous_hash'],
    }
    response = app.response_class(
        response =json.dumps(data,indent=2),
        status = 200,
        mimetype = 'application/json'
    )
    return response

# New Votes are done here
# Allows for the submission of new votes.
# Calls the new_transaction method from the blockchain.
# Returns a JSON response indicating that the transaction will be added to a specific block.
@app.route('/vote/new/<name>/<option>', methods=['GET','POST'])
def new_transaction(name,option):
    if request.method=="POST":
        """ values = request.get_json()
        # Check that the required fields are in the POST'ed data
        required = ['Party_A', 'Party_B'] """
        required=[name,option]

        # Part_A is the nominee participating in the elections
        # Party_B is the voter who votes
        if not all(k in values for k in required):
            return 'Missing values', 400

        # Create a new Transaction
        """ name=values['Party_B']
        option=values['Party_A'] """
    if name not in vote_check:
        return redirect(url_for("control",User="Voter",ID=name))
    else:
        vote_check.remove(name)

    index = blockchain.new_transaction(name, option)
    data = {
        'message': f'Transaction(The vote) will be added to Block {index}'}
    response = app.response_class(
        response = json.dumps(data,indent=2),
        status = 201,
        mimetype = 'application/json'
    )
    return response


# Displays the entire blockchain in JSON format.
@app.route('/chain/', methods=['GET'])
def full_chain():
    # Displays the whole block chain
    data = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain),
        }
    response = app.response_class(
        response = json.dumps(data,indent=2),
        status = 200,
        mimetype = 'application/json'
    )
    return response

if __name__ == '__main__':
    # App starts 
    app.run(host='localhost', port=5500, debug=True)
