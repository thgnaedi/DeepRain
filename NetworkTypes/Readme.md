# Net and Evaluation

## Categorization
The UNet was trained at firt with three and then with two categories. In the file ```categorization.py``` the converted radar data is loaded from ```Data/samplebundles```
and then split into training and validation data sets. The net is trained with the training data and validated with the other data. 

As activation function the UNet uses Softmay for hidden and output layer.

## Evaluation
To evaluate the net a confusion matrix and a ROC-curve can be generated. For each one there is a script, in which the directories to the nets must be adapted. 

### Confusion-Matrix
The script ```eval_2D_classification.py``` computes the Confusion-Matrix to a net, the variable ```directory``` has to be changed to point to your  net.

### ROC-Curve
The script ```roc_script.py``` generate the ROC-Curve with the certainty of the classes as SVG. The variables ```directory``` and ```netname``` has to be adapted.
