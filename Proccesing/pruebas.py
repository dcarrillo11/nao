import mne
import matplotlib.pyplot as plt

mne.set_log_level('error')  # reduce extraneous MNE output

# Participant ID code
p_id = 'sub-001'
data_dir = 'data/' + p_id + '/'

epochs = mne.read_epochs(data_dir + p_id + '-epo.fif', preload=True).set_montage('easycap-M1')

conditions = ['Match', 'Mismatch']

evokeds = {c:epochs[c].average() for c in conditions}

evokeds 

# define the channels we want plots for
channels = ['F1', 'FCz', 'FC2', 'C3', 'C4', 'CP1', 'CPz', 'CP2']

# create a figure with 4 subplots
fig, axes = plt.subplots(4, 2, figsize=(10, 10))

# plot each channel in a separate subplot
for idx, chan in enumerate(channels):
    mne.viz.plot_compare_evokeds(evokeds, 
                                picks=chan,
                                ylim={'eeg':(-10, 10)},
                                show_sensors='lower right',
                                legend='upper center',
                                axes=axes.reshape(-1)[idx],
                                show=False
                                )
plt.show()    