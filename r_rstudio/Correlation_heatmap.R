

# useful links: http://www.sthda.com/english/wiki/ggcorrplot-visualization-of-a-correlation-matrix-using-ggplot2


data<-read.csv(file.choose())
data
d<-data[,-1] # to remove 1st column-'year' column, it is not need to correlate
head(d)
colnames(d) <-c("MLT", "UI", "Ws", " Cs", "DMI", "SOI", "Sardine IV Quarter", "Mackerel IV Quarter", "Sardine Annual", "Mackerel Annual")
head(d)
a<-cor(d, method = "pearson", use = "complete.obs")
a

cormat <- round(cor(d),2) # 2 means two number after decimal point
head(cormat)

library(reshape2)
melted_cormat <- melt(cormat)
head(melted_cormat)
colnames(melted_cormat)<-c("Var1", "Var2", "Value")
head(melted_cormat)

library(ggplot2)
# Get lower triangle of the correlation matrix
get_lower_tri<-function(cormat){
  cormat[upper.tri(cormat)] <- NA
  return(cormat)
}
# Get upper triangle of the correlation matrix
get_upper_tri <- function(cormat){
  cormat[lower.tri(cormat)]<- NA
  return(cormat)
}

upper_tri <- get_upper_tri(cormat)
upper_tri

# Melt the correlation matrix
library(reshape2)
melted_cormat <- melt(upper_tri, na.rm = TRUE)

# Heatmap
library(ggplot2)
ggplot(data = melted_cormat, aes(Var2, Var1, fill = value))+
  geom_tile(color = "white")+
  scale_fill_gradient2(low = "blue", high = "red", mid = "white", 
                       midpoint = 0, limit = c(-1,1), space = "Lab", 
                       name="Pearson\nCorrelation") +
  theme_minimal()+ 
  theme(axis.text.x = element_text(angle = 45, vjust = 1, 
                                   size = 12, hjust = 1))+
  coord_fixed()

# REORDER MATRIX
reorder_cormat <- function(cormat){
  # Use correlation between variables as distance
  dd <- as.dist((1-cormat)/2)
  hc <- hclust(dd)
  cormat <-cormat[hc$order, hc$order]
}

# Reorder the correlation matrix
cormat <- reorder_cormat(cormat)
upper_tri <- get_upper_tri(cormat)
# Melt the correlation matrix
melted_cormat <- melt(upper_tri, na.rm = TRUE)
# Create a ggheatmap
ggheatmap <- ggplot(melted_cormat, aes(Var2, Var1, fill = value))+
  geom_tile(color = "white")+
  scale_fill_gradient2(low = "blue", high = "red", mid = "white", 
                       midpoint = 0, limit = c(-1,1), space = "Lab", 
                       name="Pearson\nCorrelation") +
  theme_minimal()+ # minimal theme
  theme(axis.text.x = element_text(angle = 90, vjust = 1, 
                                   size = 15, hjust = 1))+
  theme(axis.text.y = element_text(size = 15))+
                                   
  coord_fixed()

# Print the heatmap

print(ggheatmap)

# Add correlation coefficients on the heatmap

tiff("ocean_var&1QTR_fishery_HEATMAP.tiff", width = 12, height = 10, units = 'in', res = 300, type="cairo")
ggheatmap + 
  geom_text(aes(Var2, Var1, label = value), color = "black", size = 5) +
  theme(
    axis.title.x = element_blank(),
    axis.title.y = element_blank(),
    panel.grid.major = element_blank(),
    panel.border = element_blank(),
    panel.background = element_blank(),
    axis.ticks = element_blank(),
    legend.justification = c(1, 0),
    legend.position = c(0.6, 0.8),
    legend.direction = "horizontal")+
  guides(fill = guide_colorbar(barwidth = 12, barheight = 1,
                               title.position = "top", title.hjust = 0.5))
dev.off()

