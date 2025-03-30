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
        while self.hand_sum(self.cards) < 11:
            new_card = np.random.randint(1,11)
            #print("Player hits a card but we dont include it as a state ", new_card)
            self.cards = np.append(self.cards,new_card)

        ##print(self.dealer_cards)
        if self.hand_sum(self.cards) == 21:
            if self.hand_sum(self.dealer_cards) == 21:
                #print("Draw")
                self.game_over = True
                return 0, (self.hand_sum(self.cards), self.dealer_cards[0], self.usable_ace)
            else:
                #print("Player Won")
                self.game_over = True
                return 1, (self.hand_sum(self.cards), self.dealer_cards[0], self.usable_ace)
        return 0, (self.hand_sum(self.cards), self.dealer_cards[0], self.usable_ace)

    def play(self,HoS):
        #Player portion
        if HoS == "H":#Hit
            new_card = np.random.randint(1,11)
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
            new_card = np.random.randint(1,11)
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
        if cards.all() == self.cards.all():
            self.usable_ace = False

        while total <= 11 and num_aces > 0:
            total += 10  # upgrade Ace from 1 to 11
            num_aces -= 1
            if cards.all() == self.cards.all():
                self.usable_ace = True
        return total

#game

def policy(s): #Should return hit or stick, for a given sum, usable ace, and dealer score
    card_sum, dealer_card, usable_ace = s
    if card_sum == 21 or card_sum == 20:
        return "S"
    else:
        return "H"


num_returns = np.zeros(shape=(10,10,2))
V           = np.zeros(shape=(10,10,2))

#cuz if I V is the average of returns, = R1 + r2 + r3 + ri / N
#if I add new one, v * N + r_n+1 / N+1
#increment N
#so G is the return for the session
#V(s) = V(s) * nnum_returns(s) + G / numreturns
#numreturns + 1

def state_to_vector(s):
    card_sum, dealer_card, ace = s
    card_sum -= 11
    dealer_card -= 1
    ace = int(ace)
    return card_sum, dealer_card, ace


for i in range(10000):
    if i %1000 == 0:
        print("completed step i: ", i)
    temp = blackjack()
    states = []
    returns = []
    reward, state = temp.start()
    states.append(state)
    while reward == 0: #So we are at a nonterminal state, or a draw
        if temp.game_over == False: #We are at a non terminal state
            reward, state = temp.play(policy(state))
            returns.append(reward)
            states.append(state)
        else:
            #print("reward!: ", reward)
            break
    #print("reward!: ", reward)
    for state in states[:-1]:
        #print(state_to_vector(state))
        s = state_to_vector(state)
        V[s] = (V[s] * num_returns[s] + reward) / (num_returns[s] + 1)
        num_returns[s] += 1

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


