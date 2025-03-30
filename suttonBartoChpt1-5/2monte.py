#Okay I want to simulate one game of bs,
import numpy as np

class blackjack():
    cards = None
    dealer_cards = None
    usable_ace = False
    game_over = False
    def __init__(self):
        self.dealer_cards = None
        self.cards = None
        self.usable_ace = False
        self.game_over = False
    def start(self):
        self.cards        =  np.random.randint(1,high=11,size = (2))
        self.dealer_cards =  np.random.randint(1,high=11,size = (2))
        self.usable_ace = False
        self.game_over = False
        #print("Cards are: ", self.cards)
        while self.hand_sum(self.cards) < 12:
            new_card = self.realblackjackcard()
            #print("Player hits a card but we dont include it as a state ", new_card)
            self.cards = np.append(self.cards,new_card)

        return 0, (self.hand_sum(self.cards), self.dealer_cards[0], self.usable_ace)

    def play(self,HoS):
        #Player portion
        if HoS == "H":#Hit
            new_card = self.realblackjackcard()
            #print("Player hits an ", new_card)
            self.cards = np.append(self.cards,new_card)
            if self.hand_sum(self.cards) > 21:
                #print("player lost")
                self.game_over = True
                return -1, (self.hand_sum(self.cards), self.dealer_cards[0], self.usable_ace)
            elif self.hand_sum(self.cards) == 21:
                rew = self.dealer_play()
                return rew, (self.hand_sum(self.cards), self.dealer_cards[0], self.usable_ace)
            else: #Sum is less than 21
                #print("Player successfully hit")
                return 0, (self.hand_sum(self.cards), self.dealer_cards[0], self.usable_ace)
        elif HoS == "S": #I should just calculate for the dealer then
            #print("Player sticks on: ", self.cards)
            rew = self.dealer_play()
            return rew, (self.hand_sum(self.cards), self.dealer_cards[0], self.usable_ace)


    def dealer_play(self):
        #Dealer portion:
        while self.hand_sum(self.dealer_cards) < 17:
            new_card = self.realblackjackcard()
            #print("Dealer hits an ", new_card)
            self.dealer_cards = np.append(self.dealer_cards,new_card)
        #print("Dealer sticks on ", self.dealer_cards)
        deal = self.hand_sum(self.dealer_cards)
        play = self.hand_sum(self.cards)
        self.game_over = True

        if deal > 21:
            #print("Player won")
            return 1
        elif deal > play:
            #print("Dealer won")
            return -1
        elif deal == play:
            #print("Player tied")
            return 0
        else:
            #print("Player won")
            return 1

    def hand_sum(self,cards):
        total = np.sum(cards)
        num_aces = np.sum(cards == 1)
        if cards is self.cards:
            self.usable_ace = False

        while total <= 11 and num_aces > 0:
            total += 10  # upgrade Ace from 1 to 11
            num_aces -= 1
            if cards is self.cards:
                self.usable_ace = True
        return total
    def realblackjackcard(self):
        deck = (
            [1]*4 +             # Aces
            [2]*4 + [3]*4 + [4]*4 + [5]*4 + [6]*4 +
            [7]*4 + [8]*4 + [9]*4 + 
            [10]*16             # 10, J, Q, K (4 each)
        )
        return np.random.choice(deck)



num_returns = np.zeros(shape=(10,10,2,2))
Q           = np.zeros(shape=(10,10,2,2))

policyArr   = np.ones(shape=(10,10,2))
policyArr[9,:,0] = 1 #No matter what the dealer is showing, stick on a 9+12=21
policyArr[8,:,1] = 1 #ditto
def policy(s, epsilon=.1):
    s = state_to_vector(s)
    if np.random.rand() < epsilon:
        return np.random.choice(["H", "S"])
    if policyArr[s] == 0:
        return "H"
    else:
        return "S"

#cuz if I Q is the average of returns, = R1 + r2 + r3 + ri / N
#if I add new one, Q * N + r_n+1 / N+1
#increment N
#so G is the return for the session
#V(s) = V(s) * nnum_returns(s) + G / numreturns
#numreturns + 1

def state_to_vector(s):
    card_sum, dealer_card, ace = s
    card_sum -= 12
    dealer_card -= 1
    ace = int(ace)
    return card_sum, dealer_card, ace

length = 100000
for i in range(length):
    if i %1000 == 0:
        print("completed step i: ", i)
    temp = blackjack()
    states = []
    returns = []
    actions = []
    reward, state = temp.start()
    states.append(state)
    while reward == 0: #So we are at a nonterminal state, or a draw
        if temp.game_over == False: #We are at a non terminal state
            action = policy(state,.5*((length-i)/length)**2)
            actions.append(action)
            reward, state = temp.play(action)
            returns.append(reward)
            states.append(state)
        else:
            #print("reward!: ", reward)
            break
    #print("reward!: ", reward)
    for state, action in zip(states[:-1], actions):
        #print(state_to_vector(state))
        a = None
        if action == "H":
            a = 0
        else:
            a = 1
        
        x,y,z = state_to_vector(state)
        s = x,y,z,a

        Q[s] = (Q[s] * num_returns[s] + reward) / (num_returns[s] + 1)
        num_returns[s] += 1
    for state in states[:-1]:
        x,y,z = state_to_vector(state)
        s0 = x,y,z,0
        s1 = x,y,z,1
        if Q[s0] >= Q[s1]:
            policyArr[x,y,z] = 0
        else:
            policyArr[x,y,z] = 1

def policy_accuracy(predicted, known):
    correct = (predicted == known).sum()
    total = predicted.size
    return correct / total

vectorized_map = np.vectorize(lambda x: 'S' if x == 1 else 'H')

ResultsUsable = vectorized_map(np.flipud(policyArr[:, :, 1]))
ResultsNoUsable = vectorized_map(np.flipud(policyArr[:, :, 0]))

print("Table for Usable ace: \n", ResultsUsable)
print("Table for No Usable ace: \n", ResultsNoUsable)

usableAns =np.array(
    [['S','S','S','S','S','S','S','S','S','S'],
    ['S','S','S','S','S','S','S','S','S','S'],
    ['S','S','S','S','S','S','S','S','S','S'],
    ['H','S','S','S','S','S','S','S','H','H'],
    ['H','H','H','H','H','H','H','H','H','H'],
    ['H','H','H','H','H','H','H','H','H','H'],
    ['H','H','H','H','H','H','H','H','H','H'],
    ['H','H','H','H','H','H','H','H','H','H'],
    ['H','H','H','H','H','H','H','H','H','H'],
    ['H','H','H','H','H','H','H','H','H','H']])
 
nousableAns = np.array(
    [['S','S','S','S','S','S','S','S','S','S'],
    ['S','S','S','S','S','S','S','S','S','S'],
    ['S','S','S','S','S','S','S','S','S','S'],
    ['S','S','S','S','S','S','S','S','S','S'],
    ['S','S','S','S','S','S','S','S','S','S'],
    ['H','S','S','S','S','S','H','H','H','H'],
    ['H','S','S','S','S','S','H','H','H','H'],
    ['H','S','S','S','S','S','H','H','H','H'],
    ['H','S','S','S','S','S','H','H','H','H'],
    ['H','H','H','S','S','S','H','H','H','H']])
print("The usable-ace table has %d accuracy", policy_accuracy(ResultsUsable, usableAns))
print("The non usable-ace table has %d accuracy", policy_accuracy(ResultsNoUsable, nousableAns))

#V = #state value function. This will be the value of a state. so given a sum of 20, no usable ace, and a dealer score of 16, we get a value for it.
#So here I have used a policy, hit when 20 or 21, to get a value action family.
#I have done a polciy evaluation for each episode. Now I need to do a policy improvement
#to go the other way




#How should this work? Seems like in these mdp we should initialize with a state, and give a rward to. I get thats what the step does.
#init, should return a state and a reward
#order of the game goesi
#deal cards, __init__, return state of cards + dealer_cards one face up
#if player has natural, then compare if the dealer has natural
#return terminal state
#Otherwise player hits according to policy, play(action), so giving actions, returning with the state
#if player sum is over 21, return loss
#otherwise dealer plays according to policy
#Dealer hits 


