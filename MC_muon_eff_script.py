import uproot
import os
import argparse

import numpy as np
import ROOT

from array import array
# Sets batch mode so no popup window
ROOT.gROOT.SetBatch(True)
# Initialize parser
parser = argparse.ArgumentParser()

parser.add_argument("--input", help="Name of input file", type=str)
args = vars(parser.parse_args())
# Name of sample
sample_name= args["input"]

output_file="MC_mu_efficiencies.root"
input_file= "/eos/user/j/jreicher/SUEP/WH_private_signals/merged/"+sample_name + ".root"
# Gets sample info from input name:

# suep decay type
if "generic" in sample_name:
    decay_type="generic"
elif "hadronic" in sample_name:
    decay_type="hadronic"
else:
    decay_type="leptonic"

# dark meson (phi) mass
if "MD2.00" in sample_name:
    md = "2.00 [GeV]"
elif "MD4.00" in sample_name:
    md = "4.00 [GeV]"
elif "MD3.00" in sample_name:
    md = "3.00 [GeV]"
elif "MD8.00" in sample_name:
    md = "8.00 [GeV]"
elif "MD1.00" in sample_name:
    md = "1.00 [GeV]"
else:
    md="1.40 [GeV]"
# temperature
if "T0.25" in sample_name:
    temp = "0.25"
if "T0.35" in sample_name:
    temp = "0.35"
if "T0.50" in sample_name:
    temp = "0.50"
elif "T0.75" in sample_name:
    temp = "0.75"
elif "T1.00" in sample_name:
    temp = "1.00"
elif "T1.50" in sample_name:
    temp = "1.50"
elif "T2.00" in sample_name:
    temp = "2.00"
elif "T3.00" in sample_name:
    temp = "3.00"
elif "T4.00" in sample_name:
    temp = "4.00"
elif "T8.00" in sample_name:
    temp = "8.00"
elif "T12.00" in sample_name:
    temp = "12.00"
elif "T16.00" in sample_name:
    temp = "16.00"
elif "T32.00" in sample_name:
    temp = "32.00"
else:
    temp = "6.00"

# Gets relevant variables from file
def Events(f):
    evs=f['Events'].arrays(['HLT_IsoMu27',
                'HLT_IsoMu24',
                'HLT_Mu50',
                'Muon_pt',
                'Muon_eta',
                'Muon_dz',
                'Muon_dxy',
                'Muon_pfRelIso03_all',
                'Muon_pfRelIso03_chg',
                'Muon_looseId'])
    return evs

# Defines binning and histograms
mu_bin_edges=array('d',[0,2,4,6,8,10,12,
                         14,16,18,20,22,
                         24,26,28,30,32,
                         34,36,38,40,50,
                         60,70,80,90,100,
                         120,140,160,180,200])
# Histograms for overall efficiency
mu_totalhist=ROOT.TH1D("total_events","Total Events",len(mu_bin_edges)-1,mu_bin_edges)
mu_filthist=ROOT.TH1D("filt_events","Filtered Events",len(mu_bin_edges)-1,mu_bin_edges)

# Split into three regions of eta
eta1_mu_totalhist=ROOT.TH1D("total_events","Total Events",len(mu_bin_edges)-1,mu_bin_edges)
eta1_mu_filthist=ROOT.TH1D("filt_events","Filtered Events",len(mu_bin_edges)-1,mu_bin_edges)
eta2_mu_totalhist=ROOT.TH1D("total_events","Total Events",len(mu_bin_edges)-1,mu_bin_edges)
eta2_mu_filthist=ROOT.TH1D("filt_events","Filtered Events",len(mu_bin_edges)-1,mu_bin_edges)
eta3_mu_totalhist=ROOT.TH1D("total_events","Total Events",len(mu_bin_edges)-1,mu_bin_edges)
eta3_mu_filthist=ROOT.TH1D("filt_events","Filtered Events",len(mu_bin_edges)-1,mu_bin_edges)
# Function for filling the histograms

def muon_hists(events,etas,hists):
    mu_totalhist=hists[0]
    mu_filthist=hists[1]
    eta_min=etas[0]
    eta_max=etas[1]
    # trigger
    triggerSingleMuon = (
            events["HLT_IsoMu27"]
            | events["HLT_IsoMu24"]
            | events["HLT_Mu50"]
        )
    # quality requirements for muons
    muon_quality_check = (
                (events["Muon_looseId"])
                & (events["Muon_pt"] > 10)
                & (np.abs(events["Muon_eta"]) < 2.4)
                & (np.abs(events["Muon_dz"]) < 0.1)
                & (np.abs(events["Muon_dxy"]) < 0.02)
                & (events["Muon_pfRelIso03_chg"] < 0.25)
                & (events["Muon_pfRelIso03_all"] < 0.25)
            )
    # cut on eta
    eta_split=(
        (np.abs(events["Muon_eta"]) >= eta_min)
        & (np.abs(events["Muon_eta"]) < eta_max )
    )
    # Select based on trigger
    mu=events["Muon_pt"]
    evs=mu[muon_quality_check & eta_split]
    tr_evs=evs[triggerSingleMuon]

    #Fill histograms
    for ev in evs:
        for entry in ev:
            mu_totalhist.Fill(entry)
    for ev in tr_evs:
        for entry in ev:
            mu_filthist.Fill(entry)

    return 0

with uproot.open(input_file) as f:
    evs=Events(f)
    eta_split=[[0.0,2.4],[0.0,0.9],[0.9,2.1],[2.1,2.4]]
    eta_hists=[[mu_totalhist,mu_filthist],[eta1_mu_totalhist,eta1_mu_filthist],[eta2_mu_totalhist,eta2_mu_filthist],[eta3_mu_totalhist,eta3_mu_filthist]]
    for (etas,hists) in zip(eta_split,eta_hists):
        muon_hists(evs,etas,hists)
# Fills efficiency
eta1_effs=ROOT.TEfficiency(eta1_mu_filthist,eta1_mu_totalhist)
eta2_effs=ROOT.TEfficiency(eta2_mu_filthist,eta2_mu_totalhist)
eta3_effs=ROOT.TEfficiency(eta3_mu_filthist,eta3_mu_totalhist)
c1 = ROOT.TCanvas ("canvas","",800,600)

# Get overall Efficiency:
mu_eff=mu_filthist.Clone()
mu_eff.Sumw2()
mu_eff.Divide(mu_totalhist)
    
# Creates Efficiency Plot w legend

eta1_effs.SetTitle("Muon Trigger Efficiency in bins of pT;Muon pT [GeV];Efficiency")
legend=ROOT.TLegend(0.5,0.1,0.9,0.4)
legend.AddEntry(eta1_effs,"|#eta|<0.9","")
legend.AddEntry(eta2_effs,"0.9<|#eta|<2.1","")
legend.AddEntry(eta3_effs,"2.1<|#eta|<2.4","")
legend.AddEntry(ROOT.nullptr, temp+" [GeV], "+year,"")
legend.AddEntry(ROOT.nullptr,"SUEP decay type: "+decay_type,"")
legend.AddEntry(ROOT.nullptr,"Dark meson mass = "+ md+ " SUEP mass = 125.0 GeV","")
legend.SetTextColor(ROOT.kBlack)
legend.SetTextFont(42)
legend.SetTextSize(0.03)

# Draw plot

eta1_effs.Draw()
eta2_effs.SetLineColor(ROOT.kRed)
eta2_effs.Draw("same")
eta3_effs.SetLineColor(ROOT.kBlue)
eta3_effs.Draw("same")
legend.Draw("same")
c1.Update()
# Saves to pdf
c1.SaveAs(folder+sample_name+"_Efficiency.pdf")

# Saves overall efficiency
try:
    root_file=uproot.update(output_file)
    root_file[sample_name]=mu_eff
except (OSError, IOError) as e:
    root_file=uproot.create(output_file)
    root_file[sample_name]=mu_eff


print("sample "+sample_name+" complete")
