#ifndef EXAMPLE_DRIVER_H
#define EXAMPLE_DRIVER_H

#include <linux/kernel.h>

#define DRIVER_NAME "edev"
#define DRIVER_VERSION "0.1"

struct example_dev {
	struct pci_dev *pdev;
	struct device *dev;

	// BAR pointers
	void __iomem *bar[6];
	resource_size_t bar_len[6];

	// DMA buffer
	size_t dma_region_len;
	void *dma_region;
	dma_addr_t dma_region_addr;

	int irqcount;
};

#endif /* EXAMPLE_DRIVER_H */
