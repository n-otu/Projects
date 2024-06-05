# -*- coding: utf-8 -*-
# Sea Level Rise
# Name: Nony Otu Ugwu


import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import scipy.stats as st
from scipy.interpolate import interp1d

#####################
# Begin helper code #
#####################

def calculate_std(upper, mean):
    """
	Calculate standard deviation based on the upper 97.5th percentile

	Args:
		upper: a 1-d numpy array with length N, representing the 97.5th percentile
            values from N data points
		mean: a 1-d numpy array with length N, representing the mean values from
            the corresponding N data points

	Returns:
		a 1-d numpy array of length N, with the standard deviation corresponding
        to each value in upper and mean
	"""
    return (upper - mean) / st.norm.ppf(.975)

def load_data():
    """
	Loads data from sea_level_change.csv and puts it into numpy arrays

	Returns:
		a length 3 tuple of 1-d numpy arrays:
		    1. an array of years as ints
		    2. an array of 2.5th percentile sea level rises (as floats) for the years from the first array
		    3. an array of 97.5th percentile of sea level rises (as floats) for the years from the first array
        eg.
            (
                [2020, 2030, ..., 2100],
                [3.9, 4.1, ..., 5.4],
                [4.4, 4.8, ..., 10]
            )
            can be interpreted as:
                for the year 2020, the 2.5th percentile SLR is 3.9ft, and the 97.5th percentile would be 4.4ft.
	"""
    df = pd.read_csv('sea_level_change.csv')
    df.columns = ['Year', 'Lower', 'Upper']
    return (df.Year.to_numpy(), df.Lower.to_numpy(), df.Upper.to_numpy())


###################
# End helper code #
###################


##########
# Part 1 #
##########

def predicted_sea_level_rise(show_plot=False):
    """
	Creates a numpy array from the data in sea_level_change.csv where each row
    contains a year, the mean sea level rise for that year, the 2.5th percentile
    sea level rise for that year, the 97.5th percentile sea level rise for that
    year, and the standard deviation of the sea level rise for that year. If
    the year is between 2020 and 2100, inclusive, and not included in the data,
    the values for that year should be interpolated. If show_plot, displays a
    plot with mean and the 95% confidence interval, assuming sea level rise
    follows a linear trend.

	Args:
		show_plot: displays desired plot if true

	Returns:
		a 2-d numpy array with each row containing the year, the mean, the 2.5th
        percentile, 97.5th percentile, and standard deviation of the sea level rise
        for the years between 2020-2100 inclusive
	"""
    # first, load the data from the file
    years, slow_slr, fast_slr = load_data()

    # interpolate slow SLR and fast SLR values for years we don't have
    interp_slow = interp1d(years, slow_slr, kind='linear', fill_value='extrapolate')
    interp_fast = interp1d(years, fast_slr, kind='linear', fill_value='extrapolate')

    # initialize numpy array
    results = []
    # get the mean, slow-slr, fast-slr, and standard deviation for each year
    for year in range(2020, 2101):
        mean = (interp_slow(year) + interp_fast(year)) / 2
        slow = interp_slow(year)
        fast = interp_fast(year)
        std = calculate_std(fast, mean) # calcuate the mean
        results.append([year, mean, slow, fast, std])

    # turn list into a numpy array
    results = np.array(results)

    # now plot our data
    if show_plot:
        plt.figure(figsize=(10, 6))
        plt.plot(years, mean, label='Mean SLR', color='blue')
        plt.fill_between(years, slow, fast, color='lightblue', alpha=0.5, label='95% CI')
        plt.xlabel('Year')
        plt.ylabel('Sea Level Rise in mm')
        plt.title('Predicted Sea Level Rise with 95% Confidence Interval')
        plt.legend()
        plt.grid(True)
        plt.show()

    return results



def simulate_year(data, year, num):
    """
	Simulates the sea level rise for a particular year based on that year's
    mean and standard deviation, assuming a normal distribution.

	Args:
		data: a 2-d numpy array with each row containing a year in order from 2020-2100
            inclusive, mean, the 2.5th percentile, 97.5th percentile, and standard
            deviation of the sea level rise for the given year
		year: the year to simulate sea level rise for
        num: the number of samples you want from this year

	Returns:
		a 1-d numpy array of length num, that contains num simulated values for
        sea level rise during the year specified
	"""
    # get index for year from data
    index = np.where(data[:, 0] == year)[0]

    # if year not found, error
    if len(index) == 0:
        raise ValueError("Year not found in the data.")

    # get mean and standard deviation
    mean = data[index, 1]
    std = data[index, 4]

    # do simumlation based on normal
    simulation = np.random.normal(mean, std, size=num)

    return simulation


def plot_monte_carlo(data):
    """
	Runs and plots a Monte Carlo simulation, based on the values in data and
    assuming a normal distribution. Five hundred samples should be generated
    for each year.

	Args:
		data: a 2-d numpy array with each row containing a year in order from 2020-2100
            inclusive, mean, the 2.5th percentile, 97.5th percentile, and standard
            deviation of the sea level rise for the given year
	"""
    years = np.arange(2020, 2101)
    simulations = []

    # run 500 simulations per each year
    for year_data in data:
        mean, _, _, std_dev = year_data
        simulated_slr = np.random.normal(mean, std_dev, size=500)  # generate 500 samples based on mean and std_dev
        simulations.extend([simulated_slr] * len(years))  # extend the simulations list with 500 samples for each year

    # plot the results
    plt.figure(figsize=(10, 6))
    plt.boxplot(simulations, positions=np.tile(years, 500), showfliers=False)  # Use np.tile to repeat years for each set of 500 samples
    plt.xlabel('Year')
    plt.ylabel('Sea Level Rise in mm')
    plt.title('Monte Carlo Simulation of Sea Level Rise for 500 Simulations')
    plt.grid(True)
    plt.show()

##########
# Part 2 #
##########

def simulate_water_levels(data):
    """
	Simulates the water level for all years in the range 2020 to 2100, inclusive.

	Args:
		data: a 2-d numpy array with each row containing a year in order from 2020-2100
            inclusive, mean, the 2.5th percentile, 97.5th percentile, and standard
            deviation of the sea level rise for the given year

	Returns:
		a python list of simulated water levels for each year, in the order in which
        they would occur temporally
	"""
    water_simulation = []

    # go through every year from 2020 to 2100
    for year in range(2020, 2101):
        # simulate water level and append to the list
        slr_simulated = simulate_year(data, year, 1)
        water_simulation.append(slr_simulated[0])

    return water_simulation


def repair_only_costs(water_level_list, water_level_loss_no_prevention, house_value=500000):
    """
	Simulates the water level for all years in the range 2020 to 2100, inclusive,
    and calculates damage costs in 1000s resulting from a particular water level
    for each year dependent on a repair only strategy, where you would only pay
    to repair damage that already happened.

    The specific damage cost can be calculated using the numpy array
    water_level_loss_no_prevention, where each water level corresponds to the
    percent of property that is damaged.

    The repair only strategy is as follows:
        1) If the water level is less than or equal to 5ft, the cost is 0.
        2) If the water level is between 5ft and 10ft (exclusive), the cost is the
           house_value times the percentage of property damage for that water
           level. If the water level is not an integer value, the percentage
           should be interpolated.
        3) If the water level is at least 10ft, the cost is the entire value of
           the house.

	Args:
		water_level_list: list of simulated water levels for 2020-2100
        water_level_loss_no_prevention: a 2-d numpy array where the first column is
            the SLR levels and the second column is the corresponding property damage expected
            from that water level with no flood prevention (as an integer percentage)
        house_value: the value of the property we are estimating cost for

	Returns:
		a python list of damage costs in 1000s, in the order in which the costs would
        be incurred temporally
	"""
    # get slr levels and property damage info
    slr_levels = water_level_loss_no_prevention[:, 0]
    damage_levels = water_level_loss_no_prevention[:, 1]

    # interpolate property damage stuff
    interps = interp1d(slr_levels, damage_levels, kind='linear', fill_value='extrapolate')

    # get damage costs for each year
    damages = []
    for water_level in water_level_list:
        if water_level <= 5:
            cost = 0
        elif water_level < 10:
            frac = interps(water_level) / 100
            cost = house_value * frac
        else:
            cost = house_value
        # round, need within .1 for test case
        damages.append(round(cost / 1000, 2))

    return damages



def wait_a_bit_costs(water_level_list, water_level_loss_no_prevention, water_level_loss_with_prevention, house_value=500000,
               cost_threshold=100000):
    """
	Simulates the water level for all years in the range 2020 to 2100, inclusive,
    and calculates damage costs in 1000s resulting from a particular water level
    for each year dependent on a wait a bit to repair strategy, where you start
    flood prevention measures after having three years (not necessarily consecutive)
    with an excessive amount of damage cost.

    The specific damage cost can be calculated using the numpy array
    water_level_loss_no_prevention and water_level_loss_with_prevention, where
    each water level corresponds to the percent of property that is damaged.
    You should be using water_level_loss_no_prevention when no flood prevention
    measures are in place, and water_level_loss_with_prevention when there are
    flood prevention measures in place.

    Flood prevention measures are put into place if you have three years with a
    damage cost at least the cost_threshold.

    The wait a bit to repair only strategy is as follows:
        1) If the water level is less than or equal to 5ft, the cost is 0.
        2) If the water level is between 5ft and 10ft (exclusive), the cost is the
           house_value times the percentage of property damage for that water
           level, which is affected by the implementation of flood prevention
           measures. If the water level is not an integer value, the percentage
           should be interpolated.
        3) If the water level is at least 10ft, the cost is the entire value of
           the house.

	Args:
		water_level_list: list of simulated water levels for 2020-2100
        water_level_loss_no_prevention: a 2-d numpy array where the columns are
            water levels and the corresponding percent of property damage expected
            from that water level with no flood prevention
        water_level_loss_with_prevention: a 2-d numpy array where the columns are
            water levels and the corresponding percent of property damage expected
            from that water level with flood prevention
        house_value: the value of the property we are estimating cost for
        cost_threshold: the amount of cost incurred before flood prevention
            measures are put into place

	Returns:
		an list of damage costs in 1000s, in the order in which the costs would
        be incurred temporally
	"""
     # years over threshold
    years_over = 0

    damages = []

    for water_level in water_level_list:
        if water_level <= 5:
            cost = 0
        elif 5 < water_level < 10:
            # get damage percentage without prevention
            damage_percent = np.interp(water_level, water_level_loss_no_prevention[:, 0], water_level_loss_no_prevention[:, 1]) / 100
            # damage percentage with prevention
            if years_over >= 3:
                damage_percent = np.interp(water_level, water_level_loss_with_prevention[:, 0], water_level_loss_with_prevention[:, 1]) / 100
            cost = house_value * damage_percent
        else:
            cost = house_value

        # check if the cost exceeds the threshold
        if cost >= cost_threshold:
            years_over += 1

        damages.append(cost / 1000)

    return damages


def prepare_immediately_costs(water_level_list, water_level_loss_with_prevention, house_value=500000):
    """
	Simulates the water level for all years in the range 2020 to 2100, inclusive,
    and calculates damage costs in 1000s resulting from a particular water level
    for each year dependent on a prepare immediately strategy, where you start
    flood prevention measures immediately.

    The specific damage cost can be calculated using the numpy array
    water_level_loss_with_prevention, where each water level corresponds to the
    percent of property that is damaged.

    The prepare immediately strategy is as follows:
        1) If the water level is less than or equal to 5ft, the cost is 0.
        2) If the water level is between 5ft and 10ft (exclusive), the cost is the
           house_value times the percentage of property damage for that water
           level, which is affected by the implementation of flood prevention
           measures. If the water level is not an integer value, the percentage
           should be interpolated.
        3) If the water level is at least 10ft, the cost is the entire value of
           the house.

	Args:
		water_level_list: list of simulated water levels for 2020-2100
        water_level_loss_with_prevention: a 2-d numpy array where the columns are
            water levels and the corresponding percent of property damage expected
            from that water level with flood prevention
        house_value: the value of the property we are estimating cost for

	Returns:
		an list of damage costs in 1000s, in the order in which the costs would
        be incurred temporally
	"""
     # interpolate property damage stuff
    interp_damage_with_prevention = interp1d(water_level_loss_with_prevention[:, 0], water_level_loss_with_prevention[:, 1], kind='linear', fill_value='extrapolate')


    damage_costs = []

    # get damage costs for each year
    for water_level in water_level_list:
        if water_level <= 5:
            cost = 0
        elif 5 < water_level < 10:
            percentage = interp_damage_with_prevention(water_level)
            cost = house_value * (percentage / 100)
        else:
            cost = house_value

        # scale properly
        damage_costs.append(cost / 1000)

    return damage_costs


def plot_prep_strategies(data, water_level_loss_no_prevention, water_level_loss_with_prevention, house_value=500000,
                    cost_threshold=100000):
    """
	Runs and plots a Monte Carlo simulation of all of the different preparation
    strategies, based on the values in data and assuming a normal distribution.
    Five hundred samples should be generated for each year.

	Args:
		data: a 2-d numpy array with each row containing a year in order from 2020-2100
            inclusive, mean, the 2.5th percentile, 97.5th percentile, and standard
            deviation of the sea level rise for the given year
        water_level_loss_no_prevention: a 2-d numpy array where the columns are
            water levels and the corresponding percent of property damage expected
            from that water level with no flood prevention
        water_level_loss_with_prevention: a 2-d numpy array where the columns are
            water levels and the corresponding percent of property damage expected
            from that water level with flood prevention
        house_value: the value of the property we are estimating cost for
        cost_threshold: the amount of cost incurred before flood prevention
            measures are put into place
	"""

    # generates array of integers in this range, inclusive
    years = np.arange(2020, 2101)

    # 500 samples per year
    samples = []
    for year_data in data:
        _, mean, lower, upper, std_dev = year_data
        sample = np.random.normal(mean, std_dev, 500) # generate the 500 random samples
        sample = np.clip(sample, lower, upper)  # ensure samples stay inside the confidence interval
        samples.append(sample)

    # calculate damage costs for each strategy for each year
    repaircosts = []
    waitcosts = []
    make_now = []
    for i, sample in enumerate(samples):
        repaircosts.append(repair_only_costs(sample, water_level_loss_no_prevention, house_value))
        waitcosts.append(wait_a_bit_costs(sample, water_level_loss_no_prevention, water_level_loss_with_prevention, house_value, cost_threshold))
        make_now.append(prepare_immediately_costs(sample, water_level_loss_with_prevention, house_value))

    # plot damages for each strategy
    plt.figure(figsize=(10, 6))
    for costs, label in [(repaircosts, 'Repair Only'), (waitcosts, 'Wait a Bit'), (make_now, 'Prepare Immediately')]:
        for i in range(len(years)):
            plt.scatter([years[i]] * 500, costs[i], alpha=0.2, label=label if i == 0 else None)


    plt.plot(years, np.mean(repaircosts, axis=1), label='Mean Repair Only', color='orange')
    plt.plot(years, np.mean(waitcosts, axis=1), label='Mean Wait a Bit', color='blue')
    plt.plot(years, np.mean(make_now, axis=1), label='Mean Prepare Immediately', color='green')

    plt.xlabel('Year')
    plt.ylabel('Damage Costs in thousands')
    plt.title('Comparison of Preparation Strategies for Sea Level Rise')
    plt.legend()
    plt.grid(True)
    plt.show()



if __name__ == '__main__':
    # Comment out the 'pass' statement below to run the lines below it
    # pass

    # Uncomment the following lines to plot generate plots
    data = predicted_sea_level_rise(show_plot=False)
    water_level_loss_no_prevention = np.array([[5, 6, 7, 8, 9, 10], [0, 10, 25, 45, 75, 100]]).T
    water_level_loss_with_prevention = np.array([[5, 6, 7, 8, 9, 10], [0, 5, 15, 30, 70, 100]]).T
    # plot_monte_carlo(data)
    plot_prep_strategies(data, water_level_loss_no_prevention, water_level_loss_with_prevention)
