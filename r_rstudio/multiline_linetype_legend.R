getwd()
setwd(getwd())
d<-read.csv(file.choose())
library(ggplot2)
library(reshape2)
d
df_melt <- melt(d, id.vars='Year')  # melt by Year
df_melt

gg<- ggplot(df_melt, aes(Year, value, linetype=variable)) + geom_line(size=1.2)

gg<-gg+scale_x_continuous(breaks = seq(1992,2015,2)) 
gg<-gg+ scale_linetype_manual(name="",values=c(PM_MLT="solid", NEM_MLT="dashed"))
gg<-gg+labs(y="Degree Celcius", x ="Year", colour="MLTs") 
gg<-gg+theme_test()+theme(text=element_text(size=20, family="TT Times New Roman"))
gg<-gg + theme(legend.position = c(0.12,0.88), 
               axis.text.x = element_text(size=20, face="bold", colour = "black"),
               axis.text.y = element_text(size=20, face="bold", colour = "black"),
               axis.title.x = element_text(size=20, face="bold", colour = "black"),    
               axis.title.y = element_text(size=20, face="bold", colour = "black"))
gg<-gg + theme(legend.text=element_text(size=15, face="bold"))
gg<-gg+ theme(plot.margin = unit(c(1,1,1,1), "cm")) 
gg<-gg+theme(legend.key.size=unit(2,"lines"))
plot(gg)
tiff("PMMLT_NEMMLT_2.tiff", width = 15, height = 8.5, units = 'in', res = 300) 
plot(gg)
dev.off()
getwd()

