import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import scipy.optimize as spo

from bicycleparameters.parameter_sets import Meijaard2007ParameterSet
from data import bike_without_rider
from model import SteerControlModel

def main():

    path = "finalized_logs"
    prefix = "12-May-2023-10-11-04-bas-on-gain-6-speed-6"
    number_of_files = 3
    show_plots = False

    prefix = "12-May-2023-10-11-04-bas-on-gain-6-speed-"
    velocities = [6, 8, 10, 12, 14, 16, 18]
    eigenvalues_real = []
    eigenvalues_img = []

    for j, vel in enumerate(velocities): 
        eig_real = []
        eig_img = []
        for i in np.linspace(1, number_of_files, number_of_files, dtype=int):
            path = os.path.join("finalized_logs", "bas-on-gain-6", prefix + str(vel))
            df_gyro = pd.read_csv(path + "-gyro-" + str(i) + ".csv")

            popt, pcov = spo.curve_fit(kooijman_func,
                                df_gyro.loc[:,"time"],
                                df_gyro.loc[:,"gyro_x"],
                                p0=(0.03, -0.01, 1.0, 0.05, -0.7))
            eig_real.append(popt[1])
            eig_img.append(popt[3])

            if show_plots:
                print(popt)
                fig, ax = plt.subplots(1,1)
                ax.plot(df_gyro.index, df_gyro.loc[:,"gyro_x"], '.')
                ax.plot(df_gyro.index, kooijman_func(df_gyro.index, popt[0], popt[1], popt[2], popt[3], popt[4]))
                fig.show()
                fig.waitforbuttonpress()


        eigenvalues_real.append(sum(eig_real)/np.size(eig_real))
        eigenvalues_img.append(sum(eig_img)/np.size(eig_img))

    plot_theoretical_eigenvalues()

    print(f"Real: {eigenvalues_real}")
    print(f"Imaginary: {eigenvalues_img}")

    velocities_ms = [vel / 3.6 for vel in velocities]
    plt.plot(velocities_ms, eigenvalues_real, '.')
    plt.plot(velocities_ms, eigenvalues_img, '.')
    plt.waitforbuttonpress()


def kooijman_func(t, c1, d, c2, omega, c3):
    return c1 + np.exp(d*t) * (c2*np.cos(omega*t) + c3*np.sin(omega*t))


def period2freq(period):
    return 1.0 / period * 2.0 * np.pi


def plot_theoretical_eigenvalues():
    parameter_set = Meijaard2007ParameterSet(bike_without_rider, True)
    model = SteerControlModel(parameter_set)

    speeds = np.array([0.6, 1.0, 1.4, 2.0, 3.0, 3.2, 4.0, 4.8, 6.4, 7, 10])
    kphis = np.array([-80, -40, -25, -10, -5, -5, -5, -5, -5, -5, -5])
    kphidots = np.array([-125, -80, -65, -50, -40, -35, -20, -10, -5, -5, -5]) - 5

    f = lambda x, a, b, c: a*np.exp(b*x) + c
    kphi_pars, _ = spo.curve_fit(f, speeds, kphis, p0=[-30, -2, -0.1])
    kphidot_pars, _ = spo.curve_fit(f, speeds, kphidots, p0=[-30, -2, -0.1])

    speeds = np.linspace(0.0, 10.0, num=1000)
    kphis = f(speeds, *kphi_pars) - 1
    kphidots = f(speeds, *kphidot_pars)

    fig, ax = plt.subplots()
    ax = model.plot_eigenvalue_parts(ax=ax, v=speeds, kphi=kphis, kphidot=kphidots)
    fig.show()



if __name__ == "__main__":
    main()
