import random, math
money = 1000
def gen_dice():
    return random.randint(1,6)+random.randint(1,6)
def gen_payout():
    payout = [0]*13
    for i in range(2,13):
        payout[i] = (36/(6-abs(i-7))-1) * (1+random.gauss(0,.1))
    return payout
while(money > 0):
    die_roll = gen_dice()
    print("Your money: {0}".format(money))
    amount = [-1] * 13
    payout = gen_payout()
    print(payout[2:])
    for i in range(2,13):
        print("Pay out for {0} is {1}, your current balance is {2}".format(i,payout[i],money))
        while(amount[i] < 0 or money-amount[i] < 0):
            amount[i] = int(input())
        money -= amount[i]
    print("Roll is: {0}".format(die_roll))
    money += (payout[die_roll]+1) * amount[die_roll]