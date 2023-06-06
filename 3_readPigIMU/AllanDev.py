
import numpy as np
import math
import matplotlib.pyplot as plt


def cal_oadev(data,rate,tauArray):
	tau0 = 1/rate #Calculate the sampling period
	dataLength = data.size #Calculate N, data length
	dev = np.array([]) #Create empty array to store the output.
	actualTau = np.array([])	
	for i in tauArray:
		n = math.floor(i/tau0) #Calculate n given a tau value.
		if n == 0:
			n = 1 #Use minimal n if tau is less than the sampling period.
		currentSum = 0 #Initialize the sum
		print('n: ', n)
		for j in range(0,dataLength-2*n):
			currentSum = (data[j+2*n]-2*data[j+n]+data[j])**2+currentSum #Cumulate the sum squared
		devAtThisTau = currentSum/(2*n**2*tau0**2*(dataLength-2*n)) #Divide by the coefficient
		dev = np.append(dev,np.sqrt(devAtThisTau))
		actualTau = np.append(actualTau,n*tau0)
	return actualTau, dev #Return the actual tau and overlapped Allan deviation

NAME = '0616'
SF_A = 0.00295210451588764*1.02/2
SF_B = -0.00137052112589694
dataRate = 100

# Var = np.loadtxt(NAME, comments='#', delimiter=None, skiprows=6)
Var = np.loadtxt(NAME+'.txt', comments='#', delimiter=',', skiprows=2)
print(Var)
t = Var[:,0]
wz = Var[:,1]
# wz = Var[:,2] 
# wz_dps = wz*SF_A + SF_B
# wz_dph = 3600*(wz*SF_A + SF_B)
# thetaz = wz_dps.cumsum()/dataRate #degree
thetaz = wz.cumsum()/dataRate #degree
dataLength = t.size

print('load done')
print('N =', dataLength, end=', ')
print(thetaz.size)


tau0 = 1/dataRate
'''
tau = m*tau0
m < (N-1)/2
for N = 17697570
m < 8848785 = 8e6
'''
tauArray = np.array([tau0, 3*tau0, 5*tau0, 10*tau0, 30*tau0, 50*tau0, 
                     100*tau0, 300*tau0, 500*tau0, 1000*tau0, 3e3*tau0,
                     5000*tau0, 10000*tau0, 3e4*tau0, 50000*tau0, 100000*tau0,
					 5e5*tau0, 1e6*tau0, 2e6*tau0, 8e6*tau0])
# tauArray = np.array([tau0, 3*tau0, 5*tau0, 10*tau0, 30*tau0, 50*tau0, 
					# 100*tau0, 300*tau0, 500*tau0, 1000*tau0, 3e3*tau0,
					# 5000*tau0, 10000*tau0, 3e4*tau0, 50000*tau0, 100000*tau0,
					# 5e5*tau0])

x, y = cal_oadev(thetaz, dataRate, tauArray)
y = y*3600

plt.loglog(x,y, linestyle = '-', marker = '*')
plt.xlabel('s')
plt.ylabel('Degree/hour')
plt.grid()
plt.show()

