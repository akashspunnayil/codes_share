data<-read.csv(file.choose())
library(ggplot2)
data
ggplot(data, aes(Period,Indian_oil_sardine_Stdsd_CPUE)) + geom_bar(stat="identity")+ scale_x_continuous(breaks = seq(1998,2016,1))
ggplot(data, aes(Period,Indian_oil_sardine_Stdsd_CPUE)) + geom_bar(stat="identity")+ scale_x_continuous(breaks = seq(1998,2016,1))
#data label
ggplot(data, aes(Period,Indian_oil_sardine_Stdsd_CPUE,label=Indian_oil_sardine_Stdsd_CPUE)) + geom_bar(stat="identity")+ scale_x_continuous(breaks = seq(1998,2016,1))+geom_text()
#decrease decimal values
data$Indian_oil_sardine_Stdsd_CPUE<-round(data$Indian_oil_sardine_Stdsd_CPUE,1)
ggplot(data, aes(Period,Indian_oil_sardine_Stdsd_CPUE,label=Indian_oil_sardine_Stdsd_CPUE)) + geom_bar(stat="identity")+ scale_x_continuous(breaks = seq(1998,2016,1))+geom_text()
#aggregate data
#aggregate into yearwise (monthly mean), if Indian_oil_sardine_Stdsd_CPUE is in Monthly
data.agg<-aggregate(Indian_oil_sardine_Stdsd_CPUE ~ year,data,mean)
view(data.agg)
ggplot(data.agg, aes(Period,Indian_oil_sardine_Stdsd_CPUE,label=Indian_oil_sardine_Stdsd_CPUE)) + geom_bar(stat="identity")+ scale_x_continuous(breaks = seq(1998,2016,1))+geom_text(size=10)
#adjusting data labels
ggplot(data.agg, aes(Period,Indian_oil_sardine_Stdsd_CPUE,label=Indian_oil_sardine_Stdsd_CPUE)) + geom_bar(stat="identity")+ scale_x_continuous(breaks = seq(1998,2016,1))+geom_text(size=10, vjust=5, colour="white")
#categorised as high or low
data$cat<-ifelse(data$Indian_oil_sardine_Stdsd_CPUE>100,"High","Low")
View(data)
#aggregate and add category
data.agg<-aggregate(Indian_oil_sardine_Stdsd_CPUE ~ year+cat,data,mean)
view(data.agg)
#include category in same barplot
ggplot(data.agg, aes(Period,Indian_oil_sardine_Stdsd_CPUE,fill=cat,label=Indian_oil_sardine_Stdsd_CPUE)) + geom_bar(stat="identity")+ scale_x_continuous(breaks = seq(1998,2016,1))+geom_text(size=10, vjust=5, colour="white")









