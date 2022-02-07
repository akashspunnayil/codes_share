#aggregate data
#aggregate into yearwise (monthly mean), if Indian_oil_sardine_Stdsd_CPUE is in Monthly
data<-read.csv(file.choose())
data
d<-data[,-1] # to remove 1st column-'year' column, it is not need to correlate
head(d)
d1<-d[,-2] # to remove 2nd column-'year' column, it is not need to correlate
head(d1)
colnames(d1)<-c("Year", "MTN", "MOTHS", "MPS", "MRS", "NM", "OBBS", "OBGN", "OBOTHS", "OBRS")
d1
#a<-cbind(d1,Year, MTN, MOTHS, MPS, MRS, NM, OBBS, OBGN, OBOTHS, OBRS)
#a
data.agg<-aggregate((cbind(MTN, MOTHS, MPS, MRS, NM, OBBS, OBGN, OBOTHS, OBRS)) ~ Year,d1,mean)
data.agg
write.csv(data.agg,"SW_sardine_effort_1985-2016_annual.csv")
getwd()
