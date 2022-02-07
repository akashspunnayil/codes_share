getwd()
setwd("D:/AKASH FOLDER/Akash Works/THESIS WORKS/DATA/CATCH DATA/Final_data_Qrtrly_stdstn_sardine&mackerel/stdstn_correction")
getwd()

data<-read.csv(file.choose())
data
head(data)
#aggregate data
#aggregate into yearwise (monthly mean), if Indian_oil_sardine_Stdsd_CPUE is in Monthly
data.agg<-aggregate((cbind(sp1_OBRS)) ~ Year,data,mean)
data.agg
write.csv(data.agg,"CPUE_Agg_sp1_OBRS_GUJ.csv")


#ggplot(data.agg, aes(Period,Indian_oil_sardine_Stdsd_CPUE,label=Indian_oil_sardine_Stdsd_CPUE)) + geom_bar(stat="identity")+ scale_x_continuous(breaks = seq(1998,2016,1))+geom_text(size=10)