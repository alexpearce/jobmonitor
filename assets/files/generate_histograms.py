import ROOT as R

f = R.TFile("histograms.root", "recreate")
funcs = ["gaus", "landau", "expo", "pol1"]
titles = ["Gaussian", "Landau", "Exponential", "First order polynomial"]
limits = [(-5, 5), (-5, 10), (0, 10), (0, 10)]
for idx in range(4):
    h_name = "histogram_{0}".format(idx)
    low, high = limits[idx]
    h = R.TH1F(h_name, titles[idx], 100, low, high)
    h.FillRandom(funcs[idx % len(funcs)], 10000)
    h.Write()
f.Close()
