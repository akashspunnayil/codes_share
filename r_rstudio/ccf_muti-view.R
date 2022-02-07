data<-read.csv(file.choose())
data
variable.names=names(data)
variable.names
tiff("CCF_MACKEREL_VS_VARS.tiff", width = 10, height = 12, units = 'in', res = 300)

######## for multi-view plot #######################################################################

a<- par(mfrow=c(2,2)) # first digit is no of rows and second is no of columns
a<- par(mar=c(3,3,3,3)) # 4 side margin setting
a<- par(ps = 15, cex = 1, cex.main = 1) # ps will be the font size
#a<- for (i in 4:6)(acf(data[i], data[3],main=paste(variable.names[i]))) 
a<- for (i in 3:6)(ccf(data[i], data[2],lag.max= 15,main=paste(variable.names[i]))) 
dev.off()

####### For separate interpretaion ####################################################################

###### temporaly removing un-neccessary columns from input data for correlation ########################

d<-data[,-1] # to remove 1st column-'year' column, it is not need to correlate
head(d)
d1<-d[,-2] # to remove 2nd column-'SCPUE_Mackerel' column, it is also not need to correlate
d1

###### start correlation ##############################################################################

cor_coef = cor(d1[sapply(d1,is.numeric)], use="pairwise.complete.obs")
cor_coef
ccf(d1$SCPUE_Sardine, d1$Chl.a,lag.max= 15,main="SardinevsChl")
ccfvalues<-ccf(d1$SCPUE_Sardine, d1$Chl.a)

# if have missing values in input data
# data-na.omit(data)

ccfvalues

