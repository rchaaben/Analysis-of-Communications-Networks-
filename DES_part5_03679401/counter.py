import math
import numpy
import scipy
import scipy.stats

class Counter(object):

    """
    Counter class is an abstract class, that counts values for statistics.

    Values are added to the internal array. The class is able to generate mean value, variance and standard deviation.
    The report function prints a string with name of the counter, mean value and variance.
    All other methods have to be implemented in subclasses.
    """

    def __init__(self, name="default"):
        """
        Initialize a counter with a name.
        The name is only for better distinction between counters.
        :param name: identifier for better distinction between various counters
        """
        self.name = name
        self.values = []

    def count(self, *args):
        """
        Count values and add them to the internal array.
        Abstract method - implement in subclass.
        """
        raise NotImplementedError("Please Implement this method")

    def reset(self, *args):
        """
        Delete all values stored in internal array.
        """
        self.values = []

    def get_mean(self):
        """
        Returns the mean value of the internal array.
        Abstract method - implemented in subclass.
        """
        raise NotImplementedError("Please Implement this method")

    def get_var(self):
        """
        Returns the variance of the internal array.
        Abstract method - implemented in subclass.
        """
        raise NotImplementedError("Please Implement this method")

    def get_stddev(self):
        """
        Returns the standard deviation of the internal array.
        Abstract method - implemented in subclass.
        """
        raise NotImplementedError("Please Implement this method")

    def report(self):
        """
        Print report for this counter.
        """
        if len(self.values) != 0:
            print "Name: " + str(self.name) + ", Mean: " + str(self.get_mean()) + ", Variance: " + str(self.get_var())
        else:
            print("List for creating report is empty. Please check.")


class TimeIndependentCounter(Counter):
    
    """
    Counter for counting values independent of their duration.

    As an extension, the class can report a confidence interval and check if a value lies within this interval.
    """
    
    def __init__(self, name="default"):
        """
        Initialize the TIC object.
        """
        super(TimeIndependentCounter, self).__init__(name)
    
    def count(self, *args):
        """
        Add a new value to the internal array. Parameters are chosen as *args because of the inheritance to the
        correlation counters.
        :param: *args is the value that should be added to the internal array
        """
        self.values.append(args[0])
        
    def get_mean(self):
        """
        Return the mean value of the internal array.
        """
        # TODO Task 2.3.1: Your code goes here
        return numpy.mean(self.values)

    def get_var(self):
        """
        Return the variance of the internal array.
        Note, that we take the estimated variance, not the exact variance.
        """
        # TODO Task 2.3.1: Your code goes here
        return numpy.var(self.values, ddof=1)

    def get_stddev(self):
        """
        Return the standard deviation of the internal array.
        """
        # TODO Task 2.3.1: Your code goes here
        return numpy.std(self.values, ddof=1)

    def report_confidence_interval(self, alpha=0.05, print_report=True):
        """
        Report a confidence interval with given confidence level.
        This is done by using the t-table provided by scipy.
        :param alpha: is the confidence level (default: 95%)
        :param print_report: enables an output string
        :return: half width of confidence interval h
        """
        # TODO Task 5.1.1: Your code goes here
        return scipy.stats.t.ppf(1-alpha/2,len(self.values)-1 , self.get_mean(), math.sqrt(self.get_var()/len(self.values)))-self.get_mean()

    def is_in_confidence_interval(self, x, alpha=0.95):
        """
        Check if sample x is in confidence interval with given confidence level.
        :param x: is the sample
        :param alpha: is the confidence level
        :return: true, if sample is in confidence interval
        """
        # TODO Task 5.1.1: Your code goes here
        if x<(self.get_mean()+self.report_confidence_interval(alpha)) and x>(self.get_mean()-self.report_confidence_interval(alpha)):
            return True
        else:
            return False


class TimeDependentCounter(Counter):

    """
    Counter, that counts values considering their duration as well.

    Methods for calculating mean, variance and standard deviation are available.
    """

    def __init__(self, sim, name="default"):
        """
        Initialize TDC with the simulation it belongs to and the name.
        :param: sim is needed for getting the current simulation time.
        :param: name is an identifier for better distinction between multiple counters.
        """
        super(TimeDependentCounter, self).__init__(name)
        self.sim = sim
        self.first_timestamp = 0
        self.last_timestamp = 0

    def count(self, value):
        """
        Adds new value to internal array.
        Duration from last to current value is considered.
        """
        # TODO Task 2.3.2: Your code goes here
        self.values.append((float(self.sim.sim_state.now-self.last_timestamp),float(value)))
        self.last_timestamp = self.sim.sim_state.now

    def get_mean(self):
        """
        Return the mean value of the counter, normalized by the total duration of the simulation.
        """
        # TODO Task 2.3.2: Your code goes here
        sum=0
        for c in self.values:
            sum+=c[0]*c[1]
        return float(sum)/float(self.last_timestamp-self.first_timestamp)

    def get_var(self):
        """
        Return the variance of the TDC.
        """
        # TODO Task 2.3.2: Your code goes here
        sum=0
        for c in self.values:
            sum+=c[0]*(c[1]**2)
        return (float(sum)/float(self.last_timestamp-self.first_timestamp)) - self.get_mean()**2

    def get_stddev(self):
        """
        Return the standard deviation of the TDC.
        """
        # TODO Task 2.3.2: Your code goes here
        return self.get_var()**(0.5)

    def reset(self):
        """
        Reset the counter to its initial state.
        """
        self.first_timestamp = self.sim.sim_state.now
        self.last_timestamp = self.sim.sim_state.now
        Counter.reset(self)


class TimeIndependentCrosscorrelationCounter(TimeIndependentCounter):

    """
    Counter that is able to calculate cross correlation (and covariance).
    """

    def __init__(self, name="default"):
        """
        Crosscorrelation counter contains three internal counters containing the variables
        :param name: is a string for better distinction between counters.
        """
        super(TimeIndependentCrosscorrelationCounter, self).__init__(name)
        # TODO Task 4.1.1: Your code goes here
        self.X = TimeIndependentCounter("X")
        self.Y = TimeIndependentCounter("Y")

    def reset(self):
        """
        Reset the TICCC to its initial state.
        """
        TimeIndependentCounter.reset(self)
        # TODO Task 4.1.1: Your code goes here
        self.values = []
        self.X.reset()
        self.Y.reset()

    def count(self, x, y):
        """
        Count two values for the correlation between them. They are added to the two internal arrays.
        """
        # TODO Task 4.1.1: Your code goes here
        self.X.count(x)
        self.Y.count(y)
        self.values.append(float(x)*float(y))

    def get_cov(self):
        """
        Calculate the covariance between the two internal arrays x and y.
        :return: cross covariance
        """
        # TODO Task 4.1.1: Your code goes here
        return 1/(float(len(self.values))) * (float((sum(self.values)) - float(len(self.values))*self.X.get_mean()*self.Y.get_mean()))

    def get_cor(self):
        """
        Calculate the correlation between the two internal arrays x and y.
        :return: cross correlation
        """
        # TODO Task 4.1.1: Your code goes here
        return self.get_cov() / (math.sqrt(self.X.get_var()) * math.sqrt((self.Y.get_var())))

    def report(self):
        """
        Print a report string for the TICCC.
        """
        print "Name: " + self.name + "; covariance = " + str(self.get_cov()) + "; correlation = " + str(self.get_cor())


class TimeIndependentAutocorrelationCounter(TimeIndependentCounter):

    """
    Counter, that is able to calculate auto correlation with given lag.
    """

    def __init__(self, name="default", max_lag=10):
        """
        Create a new auto correlation counter object.
        :param name: string for better distinction between multiple counters
        :param max_lag: maximum available lag (defaults to 10)
        """
        super(TimeIndependentAutocorrelationCounter, self).__init__(name)
        # TODO Task 4.1.2: Your code goes here
        self.X = TimeIndependentCounter("X")
        self.max_lag = max_lag

    def reset(self):
        """
        Reset the counter to its original state.
        """
        TimeIndependentCounter.reset(self)
        # TODO Task 4.1.2: Your code goes here
        self.values = []
        self.X.reset()

    def count(self, x):
        """
        Add new element x to counter.
        """
        # TODO Task 4.1.2: Your code goes here
        self.X.count(float(x))

    def get_auto_cov(self, lag):
        """
        Calculate the auto covariance for a given lag.
        :return: auto covariance
        """
        # TODO Task 4.1.2: Your code goes here
        X_lag = numpy.roll(self.X.values, lag % (self.max_lag+1))
        mean = float(sum(X_lag)/len(X_lag))
        self.values = []
        for i in xrange(lag,len(self.X.values)):
            self.values.append(X_lag[i]*self.X.values[i])
        length = float(len(self.values))
        return 1/length * (sum(self.values) - length*self.X.get_mean()*self.X.get_mean())

    def get_auto_cor(self, lag):
        """
        Calculate the auto correlation for a given lag.
        :return: auto correlation
        """
        # TODO Task 4.1.2: Your code goes here
        return self.get_auto_cov(lag) / (math.sqrt(self.X.get_var()) * math.sqrt((self.X.get_var())))

    def set_max_lag(self, max_lag):
        """
        Change maximum lag. Cycle length is set to max_lag + 1.
        """
        # TODO Task 4.1.2: Your code goes here
        self.max_lag = max_lag

    def report(self):
        """
        Print report for auto correlation counter.
        """
        print "Name: " + self.name
        for i in range(0, self.max_lag+1):
            print "Lag = " + str(i) + "; covariance = " + str(self.get_auto_cov(i)) + "; correlation = " + str(self.get_auto_cor(i))