<?php 
    $page = "default";
    include 'header.php'; 
?>

<!--Property Rented (or not) Row-->
<div class="row justify-content-center text-center m-4">
    <div class="col-sm-2">
        <!-- check on which way the slash needs to be. was previously \ but now / on windows -->
        <img src="pics\shankle\shankle_front.jpg" class="d-block w-100" alt="alt text 3">
        Shankle Road: Unavailable
    </div>
    <div class="col-sm-2">
        <img src="pics\barn\barn_front.jpg" class="d-block w-100" alt="alt text 3">
        Barn Apartment: Unavailable
    </div>
    <div class="col-sm-2">
        <img src="pics\cotton\cotton_front.jpg" class="d-block w-100" alt="alt text 3">
        Cotton Street: Unavailable
    </div>
    <div class="col-sm-2">
        <img src="pics\b\signal-2021-04-09-011605_005.jpeg" class="d-block w-100" alt="alt text 3">
        Apartment B: Unavailable
    </div>
</div>

    <!--Icons Row-->
  <div class="row justify-content-center text-center m-4">
    <div class="col-sm-2 py-1">
        <div class="card bg-info text-white">
            <img class="card-img" src="pics\icons\apply.jpg" alt="Application Clipboard">
            <div class="card-body">
                <a href="app.php" class="stretched-link h5">Application</a>
            </div>
        </div>
    </div>
    <div class="col-sm-2 py-1">
        <div class="card bg-info text-success" >
            <img class="card-img" src="pics\icons\house.jpg" alt="House">
            <div class="card-body">
                <a href="property.php" class="stretched-link h5">Property Details</a>
            </div>
        </div>  
    </div>
    <div class="col-sm-2 py-1">
        <div class="card bg-info text-secondary">
            <img class="card-img" src="pics\icons\ticket.jpg" alt="Ticket">
            <div class="card-body">
                <a href="maintenance.php" class="stretched-link h5">Submit A Ticket</a>
            </div>
        </div>
    </div>
    <div class="col-sm-2 py-1">
        <div class="card bg-info text-warning">
            <img class="card-img" src="pics\icons\faq.jpg" alt="List of Questions">
            <div class="card-body">
                <a href="application.php" class="stretched-link h5">FAQ</a>
            </div>
        </div>
    </div>
  </div>



<?php 
    include 'footer.php'; 
?>