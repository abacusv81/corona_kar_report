sport=8888
gport=8888
svol=/Users/vadiraj/Project_Netapp/CaseAnal
gvol=/home/jovyan/work
docker run -p $sport:$gport -v $svol:$gvol spacy
