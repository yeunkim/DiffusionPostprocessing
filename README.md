# DiffusionPostprocessing

Performs DTIFIT and BedpostX after HCP-MPP.

## Build Docker image
Download zip file or git clone. 
```
cd DiffusionPostprocessing
docker build -t diffpost .
```

## Usage
```
docker run -ti --rm -v path/to/Diffusion/dir:/Diffusion diffpost -d /Diffusion
```
### Arguments
```
-stage [choices: all, dtifit, bedpostx] Optional. Default: all.
-d Required. Path to the Diffusion directory. i.e. /SUBJ0/SUBJ0_output/sub-SUBJ0/Diffusion/
```
