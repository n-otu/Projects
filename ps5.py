# -*- coding: utf-8 -*-
Modeling Temperature Change
# Name: Nony Otu Ugwu
# Collaborators: None

import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import r2_score
import re

# cities in our weather data
CITIES = [
    'BOSTON',
    'SEATTLE',
    'SAN DIEGO',
    'PHOENIX',
    'LAS VEGAS',
    'CHARLOTTE',
    'DALLAS',
    'BALTIMORE',
    'LOS ANGELES',
    'MIAMI',
    'NEW ORLEANS',
    'ALBUQUERQUE',
    'PORTLAND',
    'SAN FRANCISCO',
    'TAMPA',
    'NEW YORK',
    'DETROIT',
    'ST LOUIS',
    'CHICAGO'
]

TRAIN_INTERVAL = range(1961, 2000)
TEST_INTERVAL = range(2000, 2017)

##########################
#    Begin helper code   #
##########################

def standard_error_over_slope(x, y, estimated, model):
    """
    For a linear regression model, calculate the ratio of the standard error of
    this fitted curve's slope to the slope. The larger the absolute value of
    this ratio is, the more likely we have the upward/downward trend in this
    fitted curve by chance.

    Args:
        x: a 1-d numpy array with length N, representing the x-coordinates of
            the N sample points
        y: a 1-d numpy array with length N, representing the y-coordinates of
            the N sample points
        estimated: an 1-d numpy array of values estimated by a linear
            regression model
        model: a numpy array storing the coefficients of a linear regression
            model

    Returns:
        a float for the ratio of standard error of slope to slope
    """
    assert len(y) == len(estimated)
    assert len(x) == len(estimated)
    EE = ((estimated - y)**2).sum()
    var_x = ((x - x.mean())**2).sum()
    SE = np.sqrt(EE/(len(x)-2)/var_x)
    return SE/model[0]


class Dataset(object):
    """
    The collection of temperature records loaded from given csv file
    """
    def __init__(self, filename):
        """
        Initialize a Dataset instance, which stores the temperature records
        loaded from a given csv file specified by filename.

        Args:
            filename: name of the csv file (str)
        """
        self.rawdata = {}

        f = open(filename, 'r')
        header = f.readline().strip().split(',')
        for line in f:
            items = line.strip().split(',')

            date = re.match('(\d\d\d\d)(\d\d)(\d\d)', items[header.index('DATE')])
            year = int(date.group(1))
            month = int(date.group(2))
            day = int(date.group(3))

            city = items[header.index('CITY')]
            temperature = float(items[header.index('TEMP')])
            if city not in self.rawdata:
                self.rawdata[city] = {}
            if year not in self.rawdata[city]:
                self.rawdata[city][year] = {}
            if month not in self.rawdata[city][year]:
                self.rawdata[city][year][month] = {}
            self.rawdata[city][year][month][day] = temperature

        f.close()

    def get_daily_temps(self, city, year):
        """
        Get the daily temperatures for the given year and city.

        Args:
            city: city name (str)
            year: the year to get the data for (int)

        Returns:
            a 1-d numpy array of daily temperatures for the specified year and
            city
        """
        temperatures = []
        assert city in self.rawdata, "provided city is not available"
        assert year in self.rawdata[city], "provided year is not available"
        for month in range(1, 13):
            for day in range(1, 32):
                if day in self.rawdata[city][year][month]:
                    temperatures.append(self.rawdata[city][year][month][day])
        return np.array(temperatures)

    def get_temp_on_date(self, city, month, day, year):
        """
        Get the temperature for the given city at the specified date.

        Args:
            city: city name (str)
            month: the month to get the data for (int, where January = 1,
                December = 12)
            day: the day to get the data for (int, where 1st day of month = 1)
            year: the year to get the data for (int)

        Returns:
            a float of the daily temperature for the specified date and city
        """
        assert city in self.rawdata, "provided city is not available"
        assert year in self.rawdata[city], "provided year {} is not available".format(year)
        assert month in self.rawdata[city][year], "provided month is not available"
        assert day in self.rawdata[city][year][month], "provided day is not available"
        return self.rawdata[city][year][month][day]

##########################
#    End helper code     #
##########################

    def calculate_annual_temp_averages(self, cities, years):
        """
    For each year in the given range of years, computes the average of the
    annual temperatures in the given cities.

    Args:
        cities: a list of the names of cities to include in the average
            annual temperature calculation
        years: a list of years to evaluate the average annual temperatures at

    Returns:
        a 1-d numpy array of floats with length = len(years). Each element in
        this array corresponds to the average annual temperature over the given
        cities for a given year.
    """
        # NOTE: TO BE IMPLEMENTED IN PART 4B.2 OF THE PSET
        annual_temps = []

        for year in years:
            yearly_temps = []
            for city in cities:
                yearly_temps.extend(self.get_daily_temps(city, year))
            annual_temps.append(np.mean(yearly_temps))

        return np.array(annual_temps)

# Why do we choose to minimize the squared error?
# Are there other options that might be better?
#
# Write your answer below as a comment:
# We minimize the square error so to minimize the impact of outliers on our data.
# In other words, it minimizes the variance our our data. Another thing that might work better is
# we could use a robust regression technique, which might work better in a case where we
# haev a large number of outliers.

def linear_regression(x, y):
    """
    Calculates a linear regression model for the set of data points.

    Args:
        x: a 1-d numpy array of length N, representing the x-coordinates of
            the N sample points
        y: a 1-d numpy array of length N, representing the y-coordinates of
            the N sample points

    Returns:
        (m, b): A tuple containing the slope and y-intercept of the regression line,
                both of which are floats.
    """
    # get the avg of x and y
    avg_x = sum(x) / len(x)
    avg_y = sum(y) / len(y)

    # get slope
    top = sum((x[i] - avg_x) * (y[i] - avg_y) for i in range(len(x)))
    bot = sum((x[i] - avg_x) ** 2 for i in range(len(x)))
    m = top / bot

    # get y intercept
    b = avg_y - (m * avg_x)

    return (m, b)


def squared_error(x, y, m, b):
    """
    Calculates the squared error of the linear regression model given the set
    of data points.

    Args:
        x: a 1-d numpy array of length N, representing the x-coordinates of
            the N sample points
        y: a 1-d numpy array of length N, representing the y-coordinates of
            the N sample points
        m: The slope of the regression line
        b: The y-intercept of the regression line


    Returns:
        a float for the total squared error of the regression evaluated on the
        data set
    """
    # use linear regression model
    y_vals = m * x + b

    # get squared error for each data point
    squares = (y - y_vals) ** 2

    # sum up all squared errors for total
    total_squares = sum(squares)

    return total_squares


def generate_polynomial_models(x, y, degrees):
    """
    Generates a list of polynomial regression models with degrees specified by
    degrees for the given set of data points

    Args:
        x: a 1-d numpy array of length N, representing the x-coordinates of
            the N sample points
        y: a 1-d numpy array of length N, representing the y-coordinates of
            the N sample points
        degrees: a list of integers that correspond to the degree of each polynomial
            model that will be fit to the data

    Returns:
        a list of numpy arrays, where each array is a 1-d numpy array of coefficients
        that minimizes the squared error of the fitting polynomial

        The models should appear in the list in the same order as their corresponding
        integers in the `degrees` parameter
    """
    models = []

    for deg in degrees:
        coeffs = np.polyfit(x, y, deg)
        models.append(coeffs)

    return models

# How could you use generate_polynomial_models to
# return the linear regression model for a set of
# data points x,y?
#
# Write your answer below as a comment:

# We could use it by passing [1] as the degrees argument.
# Since [1] is what we use to fit a polynomial of degree 1,
# the function will return the right coefficients for the linear regression model.


def evaluate_models(x, y, models, display_graphs=False):
    """
    For each regression model, compute the R-squared value for this model and
    if display_graphs is True, plot the data along with the best fit curve. You should make a separate plot for each model.

    Your plots should adhere to the following guidelines:

        - Plot the data points as individual blue (color='C10') dots.
        - Plot the model with a red (color='C3') solid line.
        - Include a title. Your title should include the $R^2$ value of the model and the degree. If the model is a linear curve (i.e. its degree is one), the title should also include the ratio of the standard error of this fitted curve's slope to the slope. Round your $R^2$ and SE/slope values to 4 decimal places.
        - Label the axes. You may assume this function will only be used in the case where the x-axis represents years and the y-axis represents temperature in degrees Celsius.

    Args:
        x: a 1-d numpy array of length N, representing the x-coordinates of
            the N sample points
        y: a 1-d numpy array of length N, representing the y-coordinates of
            the N sample points
        models: a list containing the regression models you want to apply to
            your data. Each model is a numpy array storing the coefficients of
            a polynomial
        display_graphs: A boolean whose value specifies if the graphs should be
            displayed

    Returns:
        A list holding the R-squared value for each model
    """


    r_squares = []

    for i, model in enumerate(models):
        # get predicted y values
        y_vals = np.polyval(model, x)

        # get r^2
        r_square = r2_score(y, y_vals)
        r_squares.append(r_square)

        # make graph and plot points
        if display_graphs:
            plt.figure()
            plt.scatter(x, y, color='C10', label='Data')

            # plot curve
            poly_function = np.poly1d(model)
            plt.plot(x, poly_function(x), color='C3', label='Best Fit Curve')

            # title
            if len(model) == 2:  # if linear model
                se_over_slope = standard_error_over_slope(x, y, y_vals, model)
                plt.title(f'Degree 1: $R^2$ = {r_square:.4f}, SE/slope = {se_over_slope:.4f}')
            else:
                plt.title(f'Degree {len(model) - 1}: $R^2$ = {r_square:.4f}')

            # Axes labels
            plt.xlabel('Year')
            plt.ylabel('Temperature (°C)')

            # legend
            plt.legend()

            # display graph
            plt.show()

    return r_squares


def get_max_trend(x, y, length, positive_slope, tolerance=10**(-8)):
    """
    Args:
        x: a 1-d numpy array of length N, representing the x-coordinates of
            the N sample points
        y: a 1-d numpy array of length N, representing the y-coordinates of
            the N sample points
        length: the length of the interval
        positive_slope: a boolean whose value specifies whether to look for
            an interval with the most extreme positive slope (True) or the most
            extreme negative slope (False)
        tolerance: a floating point that tells us how close two numbers are to
            be considered equal

    Returns:
        a tuple of the form (i, j, m) such that the application of linear (deg=1)
        regression to the data in x[i:j], y[i:j] produces the most extreme
        slope m, with the sign specified by positive_slope and j-i = length.

        In the case of a tie, it returns the first interval. For example,
        if the intervals (2,5) and (8,11) both have slope 3.1, (2,5,3.1) should be returned.

        If no intervals matching the length and sign specified by positive_slope
        exist in the dataset then return None
    """

    leng = len(x)
    slope_max = None
    biggest_interval = None

    # go over all possible intervals
    for i in range(leng - length + 1):
        j = i + length
        x_interval = x[i:j]
        y_interval = y[i:j]

        # use linear regression
        slop, _ = linear_regression(x_interval, y_interval)

        # is positive?
        if (positive_slope and slop > 0) or (not positive_slope and slop < 0):
            if slope_max is None or abs(slop) > abs(slope_max):
                slope_max = slop
                biggest_interval = (i, j, slop)

    return biggest_interval


def get_all_max_trends(x, y, tolerance=10**-8):
    """
    Args:
        x: a 1-d numpy array of length N, representing the x-coordinates of
            the N sample points
        y: a 1-d numpy array of length N, representing the y-coordinates of
            the N sample points
        tolerance: a floating point that tells us how close two numbers are to
            be considered equal

    Returns:
        a list of tuples of the form (i,j,m) such that the application of linear
        regression to the data in x[i:j], y[i:j] produces the most extreme
        positive OR negative slope m, and j-i=length.

        The returned list should have len(x) - 1 tuples, with each tuple representing the
        most extreme slope and associated interval for all interval lengths 2 through len(x).
        If there is no positive or negative slope in a given interval length L (m=0 for all
        intervals of length L), the tuple should be of the form (0,L,None).

        The returned list should be ordered by increasing interval length. For example, the first
        tuple should be for interval length 2, the second should be for interval length 3, and so on.

        If len(x) < 2, return an empty list
    """
    if len(x) < 2:
        return []

    trends = []

    for length in range(2, len(x) + 1):
        slope_max = None
        biggest_interval = None

        for i in range(len(x) - length + 1):
            j = i + length
            x_interval = x[i:j]
            y_interval = y[i:j]

            # use linear regression
            slop, _ = linear_regression(x_interval, y_interval)

            # is slope most extreme
            if slope_max is None or abs(slop) > abs(slope_max):
                slope_max = slop
                biggest_interval = (i, j, slop)

        trends.append(biggest_interval if slope_max != 0 else (0, length, None))

    return trends


def calculate_rmse(y, estimated):
    """
    Calculate the root mean square error term.

    Args:
        y: a 1-d numpy array with length N, representing the y-coordinates of
            the N sample points
        estimated: an 1-d numpy array of values estimated by the regression
            model

    Returns:
        a float for the root mean square error term
    """
    # squared diff actual and estimated
    squared_diff = (y - estimated) ** 2

    # mean error squared
    mean_squared_error = np.mean(squared_diff)

    # root mean error squared
    rmse = np.sqrt(mean_squared_error)

    return rmse


def evaluate_rmse(x, y, models, display_graphs=False):
    """
    For each regression model, compute the RMSE for this model and if
    display_graphs is True, plot the test data along with the model's estimation.

    For the plots, you should plot data points (x,y) as green (color='C2') dots and your best
    fit curve (aka model) as an orange (color='C1') solid line. You should also label the axes
    of this figure appropriately and have a title reporting the following
    information:
        degree of your regression model,
        RMSE of your model evaluated on the given data points.

    RMSE should be rounded to 4 decimal places.

    Args:
        x: a 1-d numpy array with length N, representing the x-coordinates of
            the N test data sample points
        y: a 1-d numpy array with length N, representing the y-coordinates of
            the N test data sample points
        models: a list containing the regression models you want to apply to
            your data. Each model is a numpy array storing the coefficients of
            a polynomial.
        display_graphs: A boolean whose value specifies if the graphs should be
            displayed

    Returns:
        A list holding the RMSE value for each model
    """
    rmse_values = []

    for i, model in enumerate(models):
        # estimated values
        estimated_values = np.polyval(model, x)

        # rmse
        rmse = calculate_rmse(y, estimated_values)
        rmse_values.append(rmse)

        # graph data
        if display_graphs:
            plt.figure()
            plt.scatter(x, y, color='C2', label='Data')
            plt.plot(x, estimated_values, color='C1', label='Best Fit Curve')
            plt.title(f'Degree {len(model) - 1}, RMSE = {rmse:.4f}')
            plt.xlabel('X')
            plt.ylabel('Y')
            plt.legend()
            plt.show()

    return rmse_values


if __name__ == '__main__':
    pass
