# Baum Welch Algorithm
Implementation of Baum Welch-Algorithm for POS tagging.

Has implementation of both online and batch training versions.

## Usage
<code>
cd src/

python main_alter.py ../corpus/brown_nolines.txt
</code>

Other versions can be used depending on requirement. main_alter is the version used for calculating the results data.

## Tasks
 - [x] Implement Forward and Backward Algorithm.
 - [x] Compute Gamma and Eta.
 - [x] Implement Maximisation step
 - [x] Implement scaling to avoid underflow.
 - [x] Predict top 100 words(emission probabilities) for each tag.

