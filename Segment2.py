"""
This segmentation is written by others, so the source code ins't updated
"""
import subprocess, os, sys, glob
import numpy as np
import Config


def segment(config):
    print ("Start Segment")

    if "-c" in sys.argv:
        convertLikelihoodNpyToMha(config)

    pmFiles = glob.glob(config.getResultFile("pm_*.mha"))
    pmFiles.sort()
    rawFiles = []
    trustFiles = []
    initSegFiles = []
    treeFiles = []
    saliencyFiles = []
    bclabelFiles = []
    bcfeatFiles = []

    for i in range(len(pmFiles)):
        rawFiles.append("data/raw/raw_%03d.mha" % i)
        trustFiles.append("data/trust/trust_%03d.png" % i)
        initSegFiles.append(config.getResultFile("initseg_%03d.mha" % i))
        treeFiles.append(config.getResultFile("tree_%03d.ssv" % i))
        saliencyFiles.append(config.getResultFile("saliency_%03d.ssv" % i))
        bclabelFiles.append(config.getResultFile("bclabel_%03d.ssv" % i))
        bcfeatFiles.append(config.getResultFile("bcfeat_%03d.ssv" % i))

        # step 2
        subprocess.check_call(["hnsWatershed", pmFiles[i], "0.1", "0", "1", "1", initSegFiles[i]])
        # step 3
        subprocess.check_call(["hnsMerge", initSegFiles[i], pmFiles[i], "50", "200", "0.5", "0", "1", initSegFiles[i]])
        # step 4
        subprocess.check_call(["hnsGenMerges", initSegFiles[i], pmFiles[i], treeFiles[i], saliencyFiles[i]])

        # step 5
        subprocess.check_call(
            ["hnsGenBoundaryFeatures", initSegFiles[i], treeFiles[i], saliencyFiles[i], rawFiles[i], pmFiles[i],
             "data/tdict.ssv", bcfeatFiles[i]])
        # step 6
        subprocess.check_call(
            ["hnsGenBoundaryLabels", initSegFiles[i], treeFiles[i], trustFiles[i], bclabelFiles[i]])


def convertLikelihoodNpyToMha(config):
    arr = np.load(config.likelihood)
    # become number, height* width, channel
    images = arr.reshape(arr.shape[0], arr.shape[1] * arr.shape[2], 2)
    images = images.astype("float32")
    for i in range(images.shape[0]):
        with open(config.getResultFile("pm_%03d.mha" % i), "wb") as mha:
            mha.write("""ObjectType = Image
NDims = 2
BinaryData = True
BinaryDataByteOrderMSB = False
DimSize = 512 512
ElementType = MET_FLOAT
ElementDataFile = LOCAL
""")
            for j in range(images.shape[1]):
                mha.write(images[i, j, 1])

            mha.flush()


if __name__ == "__main__":
    segment(Config.load())