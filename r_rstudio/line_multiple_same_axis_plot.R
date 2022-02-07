data<-read.csv(file.choose())
data
library(ggplot2)
gg<-ggplot(data, aes(x=Year))
gg<-gg+geom_line(aes(y=SCPUE_Sardine, colour="Indian Oil Sardine SCPUE"),size=1.3)
gg<-gg+geom_line(aes(y=SCPUE_Mackerel, colour="Indian Mackerel SCPUE"),size=1.3)
gg<-gg+scale_x_continuous(breaks = seq(1985,2016,2))
gg<-gg + scale_colour_manual(values = c("red", "deepskyblue"))
gg<-gg+labs(y="SCPUE", x ="Year", colour="SCPUE")
gg<-gg+ggtitle("SCPUE of Indian Oil Sardine and Indian Mackerel along WCI")+theme_gray()+theme(text=element_text(size=28, family="Times New Roman"))
gg<-gg + theme(legend.position = c(0.5,0.89))
gg<-gg + theme(legend.text=element_text(size=25))
gg<-gg+ theme(plot.margin = unit(c(1,1,1,1), "cm"))
gg<-gg +theme(legend.key.size =  unit(0.5, "in")) # Change key size in the legend 
plot(gg)
tiff("SCPUE of sardine and Mackerel.tiff", width = 20, height = 11, units = 'in', res = 300)
plot(gg)
dev.off()


