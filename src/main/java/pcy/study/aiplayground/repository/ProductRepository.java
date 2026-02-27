package pcy.study.aiplayground.repository;

import jakarta.persistence.LockModeType;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Lock;
import org.springframework.data.jpa.repository.Query;
import pcy.study.aiplayground.entity.Product;

import java.util.Optional;

public interface ProductRepository extends JpaRepository<Product, Long> {

    @Query("SELECT p FROM Product p WHERE p.id = :id")
    @Lock(LockModeType.PESSIMISTIC_WRITE)
    Optional<Product> findByIdWithPessimisticLock(Long id);

    @Query("SELECT SUM(p.stock) FROM Product p")
    Long sumTotalStock();
}
