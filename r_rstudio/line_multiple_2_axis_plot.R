data<-read.csv(file.choose())
library(ggplot2)
data
gg<-ggplot(data, aes(x=Period))
gg<-gg+geom_line(aes(y=Indian_oil_sardine_Stdsd_CPUE, colour="Indian Oil Sardine Stdsd CPUE"),size=1.5)
gg<-gg+geom_line(aes(y=Indian_mackerel_Stdsd_CPUE, colour="Indian Mackerel Stdsd CPUE"),size=1.5)
gg<-gg+scale_x_continuous(breaks = seq(1998,2016,1))
gg<-gg + scale_colour_manual(values = c("deepskyblue", "seagreen3"))
gg<-gg+scale_y_continuous(sec.axis = sec_axis(~.*1, name = "Indian Mackerel CPUE"))  
gg<-gg+labs(y="Indian Oil Sardine CPUE", x ="Year", colour="Standardised CPUE")
gg<-gg+ggtitle("Standardised CPUE of Indian Oil Sardine and Indian Mackerel along WCI")+theme(text=element_text(size=25, family="TT Times New Roman"))
gg<-gg + theme(legend.position = c(0.12,0.93))
gg<-gg + theme(legend.text=element_text(size=15))
gg<-gg+ theme(plot.margin = unit(c(1,1,1,1), "cm"))
plot(gg)
tiff("CPUE of sardine and Mackerel.tiff", width = 12, height = 8, units = 'in', res = 300)
plot(gg)
dev.off()



