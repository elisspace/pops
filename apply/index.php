<?php 
    $page = "Home";
    include 'header.php'; 
?>

<!-- Property Grid -->
<section class="container py-3">
  <div class="row justify-content-center">
    <div class="col-12 col-lg-10">
      <div class="row g-3 row-cols-1 row-cols-sm-2 row-cols-md-3 text-center">

        <!-- Firethorn -->
        <div class="col">
          <a href="p/firethorn.php" class="text-decoration-none">
            <div class="card h-100 shadow-sm">
              <div class="ratio ratio-4x3">
                <img 
                  src="pics/firethorn/firethorn1.jpeg" 
                  class="object-fit-cover rounded-top" 
                  alt="Firethorn Way" 
                  loading="lazy">
              </div>
              <div class="card-body">
                <div class="fw-semibold">Firethorn Way</div>
                <div class="text-success fw-semibold small">Available</div>
              </div>
            </div>
          </a>
        </div>

        <!-- Rocksprings B -->
        <div class="col">
          <a href="p/rocksprings-b.php" class="text-decoration-none">
            <div class="card h-100 shadow-sm">
              <div class="ratio ratio-4x3">
                <img 
                  src="pics/rocksprings/rocksprings-front-72-perc.webp" 
                  class="object-fit-cover rounded-top" 
                  alt="Rocksprings B" 
                  loading="lazy">
              </div>
              <div class="card-body">
                <div class="fw-semibold">Rocksprings B</div>
                <div class="text-success fw-semibold small">Available</div>
              </div>
            </div>
          </a>
        </div>

        <!-- (Keep any future properties in this same card pattern)
        <div class="col">
          <a href="p/xyz.php" class="text-decoration-none">
            <div class="card h-100 shadow-sm">
              <div class="ratio ratio-4x3">
                <img src="pics/xyz/cover.webp" class="object-fit-cover rounded-top" alt="XYZ" loading="lazy">
              </div>
              <div class="card-body">
                <div class="fw-semibold">XYZ Address</div>
                <div class="text-muted fw-semibold small">Unavailable</div>
              </div>
            </div>
          </a>
        </div>
        -->

      </div>
    </div>
  </div>
</section>

<!-- Quick Actions (compact on mobile) -->
<section class="container pb-4 pt-2">
  <div class="row justify-content-center">
    <div class="col-12 col-lg-8">
      <div class="row g-3 justify-content-center">

        <!-- Application -->
        <div class="col-6 col-sm-5 col-md-4">
          <a href="app.php" class="btn btn-primary w-100 py-3 d-flex align-items-center justify-content-center gap-2 shadow-sm">
            <img 
              src="pics/icons/apply.jpg" 
              alt="Application Icon" 
              width="28" height="28" 
              class="rounded-circle object-fit-cover">
            <span class="fw-semibold">Application</span>
          </a>
        </div>

        <!-- Submit a Ticket -->
        <div class="col-6 col-sm-5 col-md-4">
          <a href="maintenance.php" class="btn btn-outline-primary w-100 py-3 d-flex align-items-center justify-content-center gap-2 shadow-sm">
            <img 
              src="pics/icons/ticket.jpg" 
              alt="Ticket Icon" 
              width="28" height="28" 
              class="rounded-circle object-fit-cover">
            <span class="fw-semibold">Submit a Ticket</span>
          </a>
        </div>

        <!-- (Optional future quick action example)
        <div class="col-6 col-sm-5 col-md-4">
          <a href="property.php" class="btn btn-light w-100 py-3 d-flex align-items-center justify-content-center gap-2 border shadow-sm">
            <img src="pics/icons/house.jpg" alt="House Icon" width="28" height="28" class="rounded-circle object-fit-cover">
            <span class="fw-semibold">Property Details</span>
          </a>
        </div>
        -->

      </div>
    </div>
  </div>
</section>

<?php 
    include 'footer.php'; 
?>

