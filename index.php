<?php 
    $page = "default";
    include 'header.php'; 
?>

    <!--First Row-->
  <div class="row justify-content-center text-center m-4">
    <div class="col-sm-4">
        <div class="card bg-info text-white">
            <img class="card-img" src="pics\icons\apply.jpg" alt="Card image">
            <div class="card-body">
                <a href="app.php" class="stretched-link h5">Application</a>
            </div>
        </div>
    </div>
    <div class="col-sm-4">
        <div class="card bg-info text-success" >
            <img class="card-img" src="pics\icons\house.jpg" alt="Card image">
            <div class="card-body">
                <a href="property.php" class="stretched-link h5">Properties</a>
            </div>
        </div>  
    </div>
  </div>
    <!-- Second Row -->
  <div class="row justify-content-center text-center m-4">
    <div class="col-sm-4">
        <div class="card bg-info text-secondary">
            <img class="card-img" src="pics\icons\ticket.jpg" alt="Card image">
            <div class="card-body">
                <a href="maintenance.php" class="stretched-link h5">Submit A Ticket</a>
            </div>
        </div>
    </div>
    <div class="col-sm-4">
        <div class="card bg-info text-warning">
            <img class="card-img" src="pics\icons\faq.jpg" alt="Card image">
            <div class="card-body">
                <a href="application.php" class="stretched-link h5">FAQ</a>
            </div>
        </div>
    </div>
  </div>

<?php 
    include 'footer.php'; 
?>