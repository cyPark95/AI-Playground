package pcy.study.aiplayground.service;

import lombok.RequiredArgsConstructor;
import org.springframework.cache.annotation.CacheEvict;
import org.springframework.cache.annotation.Cacheable;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import pcy.study.aiplayground.entity.Product;
import pcy.study.aiplayground.exception.ProductNotFoundException;
import pcy.study.aiplayground.repository.ProductRepository;

@Service
@RequiredArgsConstructor
public class ProductService {

    private final ProductRepository productRepository;

    @Transactional
    @CacheEvict(value = "stocks", allEntries = true)
    public void orderProduct(Long productId, int quantity) {
        Product product = productRepository.findByIdWithPessimisticLock(productId)
                .orElseThrow(ProductNotFoundException::new);

        product.decreaseStock(quantity);
    }

    @Transactional(readOnly = true)
    @Cacheable(value = "stocks")
    public long getTotalStockValue() {
        return productRepository.sumTotalStock();
    }
}
