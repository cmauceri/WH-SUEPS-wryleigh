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
parser.add_argument("--era", help="data era", type=str)
#parser.add_argument("--input")
args = vars(parser.parse_args())
input_file = "local.root"
year=args["era"]
output_file= "out.root"
# Gets relevant variables from file
def Events(f):
    evs=f['Events'].arrays(['HLT_IsoMu27',
                'HLT_Mu50',
                'Muon_pt',
                'Muon_eta',
                'Muon_dz',
                'Muon_dxy',
                'Muon_pfRelIso03_all',
                'Muon_pfRelIso03_chg',
                'Muon_mediumId',
                'Flag_goodVertices',
                'Flag_globalSuperTightHalo2016Filter',
                'Flag_HBHENoiseFilter',
                'Flag_HBHENoiseIsoFilter',
                'Flag_EcalDeadCellTriggerPrimitiveFilter',
                'Flag_BadPFMuonFilter',
                'Flag_BadPFMuonDzFilter',
                'Flag_eeBadScFilter',
                'Flag_ecalBadCalibFilter'])

    return evs

# Defines binning and histograms
mu_bin_edges=array('d',[0,2,4,6,8,10,12,
                         14,16,18,20,22,
                                                 24,26,28,30,32,
                         34,36,38,40,50,
                         60,70,80,90,100,
                         120,140,160,180,200])

# Split into three regions of eta
eta1_mu_num=ROOT.TH1D("eta_1_num","Muon events passing trigger eta region 1",len(mu_bin_edges)-1,mu_bin_edges)
eta1_mu_denom=ROOT.TH1D("eta1_denom","Total Muon Events eta region 1",len(mu_bin_edges)-1,mu_bin_edges)
eta2_mu_num=ROOT.TH1D("eta2_num","Muon events passing trigger eta region 2",len(mu_bin_edges)-1,mu_bin_edges)
eta2_mu_denom=ROOT.TH1D("eta2_denom","Total Muon Events eta region 2",len(mu_bin_edges)-1,mu_bin_edges)
eta3_mu_num=ROOT.TH1D("eta3_num","Muon events passing trigger eta region 3",len(mu_bin_edges)-1,mu_bin_edges)
eta3_mu_denom=ROOT.TH1D("eta3_denom","Total Muon Events eta region 3",len(mu_bin_edges)-1,mu_bin_edges)
eta_hists=[[eta1_mu_num,eta1_mu_denom],[eta2_mu_num,eta2_mu_denom],[eta3_mu_num,eta3_mu_denom]]

# Function for filling the histograms

def muon_hists(events,etas,hists,year):
    mu_num=hists[0]
    mu_denom=hists[1]
    eta_min=etas[0]
    eta_max=etas[1]
    # trigger
    triggerSingleMuon = (
            events["HLT_IsoMu27"]
            | events["HLT_Mu50"]
        )
    # quality requirements for muons
    if year =="2018" or year =="2017":
        muon_quality_check = (
            (events['Flag_goodVertices'])
            &(events['Flag_globalSuperTightHalo2016Filter'])
            &(events['Flag_HBHENoiseFilter'])
            &(events['Flag_HBHENoiseIsoFilter'])
            &(events['Flag_EcalDeadCellTriggerPrimitiveFilter'])
            &(events['Flag_BadPFMuonFilter'])
            &(events['Flag_BadPFMuonDzFilter'])
            &(events['Flag_eeBadScFilter'])
            &(events['Flag_ecalBadCalibFilter'])
            &(events["Muon_mediumId"])
            & (events["Muon_pt"] > 10)
            & (np.abs(events["Muon_eta"]) < 2.4)
                        & (np.abs(events["Muon_dz"]) < 0.1)
            & (np.abs(events["Muon_dxy"]) < 0.02)
            & (events["Muon_pfRelIso03_chg"] < 0.25)
            & (events["Muon_pfRelIso03_all"] < 0.25)
        )
    else:
        muon_quality_check = (
            (events['Flag_goodVertices'])
            &(events['Flag_globalSuperTightHalo2016Filter'])
            &(events['Flag_HBHENoiseFilter'])
            &(events['Flag_HBHENoiseIsoFilter'])
            &(events['Flag_EcalDeadCellTriggerPrimitiveFilter'])
            &(events['Flag_BadPFMuonFilter'])
            &(events['Flag_BadPFMuonDzFilter'])
            &(events['Flag_eeBadScFilter'])
            &(events["Muon_mediumId"])
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
            mu_denom.Fill(entry)
    for ev in tr_evs:
        for entry in ev:
            mu_num.Fill(entry)
            
    return 0

with uproot.open(input_file) as f:
    evs=Events(f)
    eta_split=[[0.0,0.9],[0.9,2.1],[2.1,2.4]]
    for (etas,hists) in zip(eta_split,eta_hists):
        muon_hists(evs,etas,hists,year)
print("debugging")
print("num1")
print(type(eta1_mu_num))
print("denom 1")
print(type(eta1_mu_denom))
c1 = ROOT.TCanvas ("canvas","",800,600)
eta1_mu_denom.Draw()
c1.Update()
c1.SaveAs("Efficiency.png")
# Saves overall efficiency
root_file = ROOT.TFile(output_file,"RECREATE")
root_file.cd()
eta1_mu_num.Write()
eta1_mu_denom.Write()
eta2_mu_num.Write()
eta2_mu_denom.Write()
eta3_mu_num.Write()
eta3_mu_denom.Write()

root_file.Close()

print("sample complete")
                        
