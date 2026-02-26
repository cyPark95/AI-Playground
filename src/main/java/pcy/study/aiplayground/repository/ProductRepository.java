package pcy.study.aiplayground.repository;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import pcy.study.aiplayground.entity.Product;

public interface ProductRepository extends JpaRepository<Product, Long> {

    @Query("SELECT SUM(p.stock) FROM Product p")
    Long sumTotalStock();
}
