data<-read.csv(file.choose())
library(ggplot2)
data
ggplot(data, aes(Period,Indian_oil_sardine_Stdsd_CPUE)) + geom_bar(stat="identity")+ scale_x_continuous(breaks = seq(1998,2016,1))









