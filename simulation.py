# imports
import numpy as np
import random
from brownian_motion import simulate_brownian_motion
from transaction_helper import payment_selection

# Define a simulation environment


class Simulation:

    # Not sure how accurate these motions with these initials will be
    def __init__(self):
        # Interest rate (%)
        self.interest_rate = simulate_brownian_motion(initial=0.05, mu=0, sigma=0.01)
        # Inflation rate (%)
        self.inflation = simulate_brownian_motion(initial=0.02, mu=0.00, sigma=0.005)
        # Stock appreciation, modelled roughly after S&P 500.
        # -- NOTE -- Let's add some market cycles to simulate bear + bull markets.
        self.cash_appreciation = simulate_brownian_motion(initial=1, mu=0.083, sigma=0.1589)

    @staticmethod
    def new_properties():
        return [Property() for i in range(3)]   # get array of 3 properties




# Class to generate random real estate property
# Remember to incorporate inflation and interest rates to these properties
class Property:
    def __init__(self):
        # Init randomized property attributes
        self.purchase_price = abs(np.random.normal(500000,200000))
        self.rent_yield = np.random.normal(.075, .025)
        self.expenses_rate = abs(np.random.normal(.3, .1)) # Might change

        #---Appreciation Options----
        # Beta relative to global randomized market variable
        #self.appreciation_rate = np.random.normal(.02, .4)
        # Fixed appreciation

        # Init decision-based attributes
        self.price = self.purchase_price
        self.appreciation_rate = 0.025/12
        self.interest_rate = 1
        self.down_payment = 1
        self.loan_outstanding = 1
        self.term_length = 1
        self.status = 0 # 0 means can buy, 1 means owned
        self.cash_flow = 0
        self.accrued_gains = 0
        self.total_monthly_payments, self.monthly_interest_payments, self.monthly_principal_payments = mortgage_financials(self.purchase_price, self.down_payment, self.interest_rate, self.term_length, self.loan_outstanding)


# ---- Mortgage Calculator----
# Outputs mortgage payment amounts based on remaining loan to be paid off, term length and original loan recieved
def mortgage_financials(purchase_price, down_payment, interest_rate, months, loan_outstanding):
    # Amount borrowed
    original_loan = purchase_price - down_payment
    # Interest rate, assuming monthly payments
    monthly_interest_rate = interest_rate/12

    # Monthly Payment = P * I * [(1+I)^t / (1+i)^t -1]
    total_monthly_payments = original_loan * monthly_interest_rate * ((1+monthly_interest_rate)**months/((1+monthly_interest_rate)**months-1))

    # Interest Payment = remaining loan * interest rate
    monthly_interest_payments = loan_outstanding * monthly_interest_rate

    # Principal Payment makes up remainder of mortgage payment
    monthly_principal_payments = total_monthly_payments - monthly_interest_payments

    return total_monthly_payments, monthly_interest_payments, monthly_principal_payments

    # Updates property attributes monthly, incl. mortgage payments, property value, cash flow

def update_properties(owned_property_array):
    # Iterates through list of owned properties
    for i in range(len(owned_property_array)):
        # Updates pricing by monthly appreciation rate
        owned_property_array[i].price = owned_property_array[i].price * (
                1 + owned_property_array[i].appreciation_rate)
        # If mortgage isn't paid off, continues to update mortgage payments.
        if owned_property_array[i].loan_outstanding != 0:
            # Updates mortgage payment amounts
            owned_property_array[i].total_monthly_payments, owned_property_array[i].monthly_interest_payments, \
            owned_property_array[i].monthly_principal_payments = mortgage_financials(
                owned_property_array[i].purchase_price, owned_property_array[i].down_payment,
                owned_property_array[i].interest_rate,
                owned_property_array[i].term_length, owned_property_array[i].loan_outstanding)
            # Reduces loan outstanding, by amount paid off during the month
            owned_property_array[i].loan_outstanding = owned_property_array[i].loan_outstanding - \
                                                       owned_property_array[
                                                           i].monthly_principal_payments

        # Month after mortgage is paid off/If mortgage is gone
        else:
            owned_property_array[i].total_monthly_payments = 0
            owned_property_array[i].monthly_principal_payments = 0
            owned_property_array[i].monthly_interest_payments = 0

        # Rounds small loan outstanding to 0, same month that mortgage finishes. Last month of term
        if owned_property_array[i].loan_outstanding < 10:
            owned_property_array[i].loan_outstanding = 0

        # Cash Flow = Rent - Expenses - Mortgage Payments
        owned_property_array[i].cash_flow = owned_property_array[i].rent_yield / 12 * owned_property_array[
            i].purchase_price * (1 - owned_property_array[i].expenses_rate) - owned_property_array[
                                                i].total_monthly_payments

# Receives decision from player or agent on current property shown
def decision(property, financial_accounts, interest_rate, owned_properties, index, n_dels):

    total_liquid_assets = financial_accounts.tfsa + financial_accounts.rrsp + financial_accounts.investing_account + financial_accounts.cash_account

    # Shows options to player
    print("""
        1. Mortgage, 20 year + 20% down payment (${0:,.2f})
        2. Mortgage, 30 year + 20% down payment (${0:,.2f})
        3. Buy Outright
        4. Sell
        5. Refinance
        6. Pass
                   """.format(property.purchase_price * 0.2))

    # Receives input from keyboard (or agent later)
    dec = input("Decision:")

    # Init Variable
    capital_gains = 0
    rrsp_used = 0
    investment_used = 0

    # --- Decision effects ---
    # Mortgage, 20 year + 20% down
    if dec == '1' and property.status == 0 and total_liquid_assets >= property.purchase_price * 0.2:
        # Alters attributes to reflect mortgage type + owned status
        property.interest_rate = interest_rate  # can add 1% onto rate due to fixed rates being higher, number is placeholder
        property.down_payment = property.purchase_price * 0.2
        property.loan_outstanding = property.purchase_price - property.down_payment
        property.status = 1
        property.term_length = 240

        # Adds new property to list of owned properties, removes down payment from cash account
        #total_liquid_assets = total_liquid_assets - property.purchase_price * 0.2
        financial_accounts, investment_used, rrsp_used = payment_selection(financial_accounts, property.purchase_price * 0.2)

        owned_properties.append(property)

    # Mortgage, 30 year + 20% down
    elif dec == '2' and property.status == 0 and total_liquid_assets >= property.purchase_price * 0.2:
        # Alters attributes to reflect mortgage type + owned status
        property.interest_rate = interest_rate  # can add 1% onto rate due to fixed rates being higher, number is placeholder
        property.down_payment = property.purchase_price * 0.2
        property.loan_outstanding = property.purchase_price - property.down_payment
        property.term_length = 360
        property.status = 1

        # Adds new property to list of owned properties, removes down payment from cash account
        #total_liquid_assets = total_liquid_assets - property.purchase_price * 0.2
        financial_accounts, investment_used, rrsp_used = payment_selection(financial_accounts, property.purchase_price * 0.2)
        owned_properties.append(property)

    # Bought in full, no mortgage
    elif dec == '3' and property.status == 0 and total_liquid_assets >= property.purchase_price:
        # Alters attributes to reflect mortgage type (or lack thereof) + owned status
        property.interest_rate = interest_rate  # can add 1% onto rate due to fixed rates being higher, number is placeholder
        property.down_payment = property.purchase_price
        property.loan_outstanding = 0
        property.term_length = 360
        property.status = 1

        # Adds new property to list of owned properties, removes full purchase price from cash account
        #total_liquid_assets = total_liquid_assets - property.purchase_price
        financial_accounts, investment_used, rrsp_used = payment_selection(financial_accounts, property.purchase_price)
        owned_properties.append(property)

    # Sells property
    elif dec == '4' and property.status == 1:
        # Adds change in property value since purchase/refinance to capital gains account
        capital_gains = property.accrued_gains + property.price - property.purchase_price

        # Pre-allocated cash account increased by difference between sale price and amount of debt still owing
        financial_accounts.remaining_cash = financial_accounts.remaining_cash + property.price - property.loan_outstanding - capital_gains

        # Future Note: return gains to main.py or taxes.

        # Property removed from list of owned properties.
        # N_dels keeps track of how many properties have been deleted that month to avoid index running out of bounds.
        owned_properties.pop(index - n_dels)
        n_dels = n_dels + 1

    # Refinances property, leaves 20% of property value in as equity
    elif dec == '5' and property.status == 1:
        # Cash account increased by difference between property value and the sum of debt owing and 20% down payment
        financial_accounts.remaining_cash = financial_accounts.remaining_cash + property.price - property.loan_outstanding - property.price * 0.2
        # Resets the property attributes, to reflect the new mortgage
        property.accrued_gains = property.price - property.purchase_price  # Tracks capital gains
        property.purchase_price = property.price  # Resets house with refinance
        property.interest_rate = interest_rate  # can add 1% onto rate due to fixed rates being higher, number is placeholder
        property.down_payment = property.purchase_price * 0.2
        property.loan_outstanding = property.purchase_price - property.down_payment
        property.term_length = 360
        # Replaces old property object with new object to alter mortgage
        owned_properties[index] = property

    # Hold, no decision, nada.
    elif dec == '6':
        pass
    # Catches invalid/bad decisions
    # Can't afford property, sell property not owned, buy property already owned etc.
    # Will prune ML choices that end up here with punishment
    else:
        print("Invalid Choice")
    # Returns updated cash account and # of properties sold thus far in the month
    return financial_accounts, n_dels, capital_gains, rrsp_used, investment_used




