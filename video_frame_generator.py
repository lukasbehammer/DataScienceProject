# Copyright (c) 2023, Lukas Behammer
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.

from multiprocessing import Pool
from Main import timeseries_pearson_corr
from Import import img_data_loader, get_parcellation_data
from Visualization import create_network_graph_frames
import nilearn.image as nimg
from glob import glob
import numpy as np
import itertools

# setup
patients = ["100307", "100408", "101107", "101309", "101915", "103111", "103414", "103818", "105014", "105115",
            "106016", "108828", "110411", "111312", "111716", "113619", "113922", "114419", "115320", "116524",
            "117122", "118528", "118730", "118932", "120111", "122317", "122620", "123117", "123925", "124422",
            "125525", "126325", "127630", "127933", "128127", "128632", "129028", "130013", "130316", "131217",
            "131722", "133019", "133928", "135225", "135932", "136833", "138534", "139637", "140925", "144832",
            "146432", "147737", "148335", "148840", "149337", "149539", "149741", "151223", "151526", "151627",
            "153025", "154734", "156637", "159340", "160123", "161731", "162733", "163129", "176542", "178950",
            "188347", "189450", "190031", "192540", "196750", "198451", "199655", "201111", "208226", "211417",
            "211720", "212318", "214423", "221319", "239944", "245333", "280739", "298051", "366446", "397760",
            "414229", "499566", "654754", "672756", "751348", "756055", "792564", "856766", "857263", "899885"]
patient_id = "100307"
patient_num = patients.index(patient_id)

sagittal_slice = 70
coronal_slice = 70
transversal_slice = 45

slices = (coronal_slice, sagittal_slice, transversal_slice)

correlation_threshold = 0.75

# import all timeseries
files = glob("N:/HCP/Unrelated 100/Patients/timeseries/*")
all_timeseries = [np.load(file) for file in files]
len(all_timeseries)

# load atlas data
region_maps, region_maps_data, masked_aal, regions, region_labels = get_parcellation_data(fetched=True)

# load Average T1w Image
path_T1w = "./Data/S1200_AverageT1w_restore.nii.gz"
img_T1w, img_data_T1w = img_data_loader(path_T1w)

# import all centroids
files = glob("./Data/centroids/*")
all_centroids = np.concatenate([np.load(file) for file in files], axis=0)

# resample Images to region labels
resampled_img_data_T1w = nimg.resample_to_img(img_T1w, region_maps, interpolation='nearest').get_fdata()

timeseries = all_timeseries[patient_num]
# compute correlation between regions in sliding window
correlation_matrices_per_patient = timeseries_pearson_corr(timeseries, step_width=5, overlap_percentage=0.2)

# set diagonal to 0 (no correlation of region with itself), compute absolute value to have only positive
# correlations and set all values <= threshold to 0
for k in np.arange(len(correlation_matrices_per_patient)):
    for l in np.arange(len(regions)):
        correlation_matrices_per_patient[k][l,l] = 0
correlation_matrices_per_patient_abs = np.abs(correlation_matrices_per_patient)
correlation_matrices_per_patient_abs_thresh = correlation_matrices_per_patient_abs * \
                                              (correlation_matrices_per_patient_abs > correlation_threshold)

p1 = correlation_matrices_per_patient_abs_thresh[0:25, :, :]
p2 = correlation_matrices_per_patient_abs_thresh[25:50, :, :]
p3 = correlation_matrices_per_patient_abs_thresh[50:75, :, :]
p4 = correlation_matrices_per_patient_abs_thresh[75:100, :, :]
p5 = correlation_matrices_per_patient_abs_thresh[100:125, :, :]
p6 = correlation_matrices_per_patient_abs_thresh[125:150, :, :]
p7 = correlation_matrices_per_patient_abs_thresh[150:175, :, :]
p8 = correlation_matrices_per_patient_abs_thresh[175:200, :, :]
p9 = correlation_matrices_per_patient_abs_thresh[200:225, :, :]
p10 = correlation_matrices_per_patient_abs_thresh[225:250, :, :]
p11 = correlation_matrices_per_patient_abs_thresh[250:275, :, :]
p12 = correlation_matrices_per_patient_abs_thresh[275:300, :, :]

matrices = [p1, p2, p3, p4, p5, p6, p7, p8, p9, p10, p11, p12]

create_network_graph_frames(resampled_img_data_T1w, (coronal_slice, sagittal_slice, transversal_slice), correlation_matrices_per_patient_abs_thresh, all_centroids, regions, region_labels)
