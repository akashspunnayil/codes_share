# in inches
tiff("CPUE of sardine and Mackerel.tiff", width = 12, height = 8, units = 'in', res = 300, type="cairo") # type = "cairo" will help from error
plot(gg)
dev.off()

# in pixels
tiff("Interannual variability.tif",width = 3600, height = 2400, units = 'px', res = 300)
plot(gg)
dev.off()