<?php 
    $page = "Home";
    include 'header.php'; 
?>

<!--Property Rented (or not) Row 1-->
<div class="row justify-content-center text-center m-2 row-cols-3">
    <!-- <div class="col">
        <a href="p/shankle.php"><img src="pics/shankle/shankle_front_3_perc.webp" class="d-block w-100" alt="Shankle Road"></a>
        Shankle Road: <b>Unavailable</b>
    </div> -->
<!--    <div class="col">
       <a href="p/barn.php"><img src="pics/barn/barn_front_0_perc.webp" class="d-block w-100" alt="Barn Apartment"></a>
        Barn Apartment
    </div> -->
    <!-- <div class="col">
       <a href="p/cotton.php"> <img src="pics/cotton/cotton_front_0_perc.webp" class="d-block w-100" alt="Cotton Street"></a>
        Cotton Street: <b>Unavailable</b>
    </div> -->

<!-- Row 2 -->
    <!-- <div class="col">
       <a href="p/b.php"> <img src="pics/b/signal-2021-04-09-011605_001.jpeg" class="d-block w-100" alt="Trailer Lot B"></a>
        Trailer Lot B: <b>Unavailable</b>
    </div> -->
<!--
    <div class="col">
       <a href="p/d.php"> <img src="pics/d/lot-d-front-20-perc.webp" class="d-block w-100" alt="Trailer Lot D"></a>
        Trailer Lot D
    </div> --> 
    <!-- <div class="col">
       <a href="p/e.php"> <img src="pics/e/lot-e-72-perc.webp" class="d-block w-100" alt="Trailer Lot E"></a>
        Trailer Lot E: <b>Unavailable</b>
    </div> -->

<!-- Row 3 -->
    <!-- <div class="col">
    <a href="p/rocksprings-a.php"><img src="pics/rocksprings/rocksprings-front-72-perc.webp" class="d-block w-100" alt="Rocksprings A"></a>
        Rocksprings A: <b>Unavailable</b>
    </div> -->
    <div class="col">
    <a href="p/rocksprings-b.php"><img src="pics/rocksprings/rocksprings-front-72-perc.webp" class="d-block w-100" alt="Rocksprings B"></a>
        Rocksprings B: <b>Available</b>
    </div> 
    <div class="col">
       <a href="p/cottage.php"> <img src="pics/cottage/cottage_front_0_perc.webp" class="d-block w-100" alt="Barn Cottage"></a>
        Barn Cottage: <b>Available</b>
    </div>
</div> 

    <!--Icons Row-->
  <div class="row justify-content-center text-center m-4">
    <div class="col py-1">
        <div class="card bg-info text-white">
            <img class="card-img" src="pics\icons\apply.jpg" alt="Application Clipboard">
            <div class="card-body">
                <a href="app.php" class="stretched-link h5">Application</a>
            </div>
        </div>
    </div>
    <!-- <div class="col-sm-2 py-1">
        <div class="card bg-info text-success" >
            <img class="card-img" src="pics\icons\house.jpg" alt="House">
            <div class="card-body">
                <a href="property.php" class="stretched-link h5">Property Details</a>
            </div>
        </div>  
    </div> -->
    <div class="col py-1">
        <div class="card bg-info text-secondary">
            <img class="card-img" src="pics\icons\ticket.jpg" alt="Ticket">
            <div class="card-body">
                <a href="maintenance.php" class="stretched-link h5">Submit A Ticket</a>
            </div>
        </div>
    </div>
    <!-- <div class="col py-1">
        <div class="card bg-info text-warning">
            <img class="card-img" src="pics\icons\faq.jpg" alt="List of Questions">
            <div class="card-body">
                <a href="application.php" class="stretched-link h5">FAQ</a>
            </div>
        </div>
    </div> -->
  </div>



<?php 
    include 'footer.php'; 
?>
