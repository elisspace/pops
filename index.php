<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Gaultney Management — Professional Services</title>
  <meta name="description" content="Professional services by Mark Gaultney. Reliable, transparent, and client-first." />
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
  <style>
    :root{
      --brand:#0d6efd; /* bootstrap primary */
      --ink:#1f2937;  /* slate-800 */
      --muted:#6b7280;/* slate-500 */
      --bg:#f8fafc;   /* slate-50 */
    }
    body{color:var(--ink); background:var(--bg);}    
    .nav-link, .navbar-brand{font-weight:600}
    .btn-cta{box-shadow:0 8px 20px rgba(13,110,253,.2)}
    .hero{
      background:linear-gradient(180deg, #ffffff 0%, #eef5ff 100%);
      border-bottom:1px solid #e5e7eb;
    }
    .section-title{font-weight:800; letter-spacing:.3px}
    .small-link{font-size:.875rem; color:var(--muted)}
    .list-timeline{position:relative; padding-left:1.5rem}
    .list-timeline::before{content:""; position:absolute; left:.4rem; top:.25rem; bottom:.25rem; width:2px; background:#dbeafe}
    .list-timeline li{margin-bottom:1rem;}
    .list-timeline li::marker{content:""}
    .bullet{display:inline-block; width:.65rem; height:.65rem; border-radius:50%; background:var(--brand); margin-right:.5rem}
    .card-placeholder{background:#f1f5f9; border:1px dashed #cbd5e1; height:140px;}
    footer a{color:#0d6efd; text-decoration:none}
    footer a:hover{text-decoration:underline}
  </style>
</head>
<body>
  <!-- NAVBAR -->
  <nav class="navbar navbar-expand-lg bg-white sticky-top border-bottom">
    <div class="container">
      <a class="navbar-brand" href="#top">Gaultney Management</a>
      <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#nav" aria-controls="nav" aria-expanded="false" aria-label="Toggle navigation">
        <span class="navbar-toggler-icon"></span>
      </button>
      <div class="collapse navbar-collapse" id="nav">
        <ul class="navbar-nav ms-auto mb-2 mb-lg-0">
          <li class="nav-item"><a class="nav-link" href="#about">About</a></li>
          <li class="nav-item"><a class="nav-link" href="#contact">Contact</a></li>
        </ul>
        <div class="d-flex gap-2 ms-lg-3">
          <a class="btn btn-primary btn-sm btn-cta" href="https://www.linkedin.com/in/mark-gaultney/" target="_blank" rel="noopener" aria-label="LinkedIn profile">Connect on LinkedIn</a>
        </div>
      </div>
    </div>
  </nav>

  <!-- HERO -->
  <header id="top" class="hero py-5 py-lg-6">
    <div class="container py-4">
      <div class="row align-items-center g-4">
        <div class="col-lg-7">
          <h1 class="display-5 fw-bold">JD Edwards Services</h1>
          <p class="lead mt-3">Clear scope. On-time delivery. Practical results. I help clients move from plan to execution with a calm, process-driven approach.</p>
          <div class="d-flex flex-wrap gap-2 mt-3">
            <a class="btn btn-primary btn-lg btn-cta" href="https://www.linkedin.com/in/mark-gaultney/" target="_blank" rel="noopener">View Profile on LinkedIn</a>
            <a class="btn btn-outline-primary btn-lg" href="#contact">Contact Me</a>
          </div>
        </div>
        <div class="col-lg-5">
          <div class="card shadow-sm border-0">
            <div class="card-body">
              <h2 class="h5 mb-3">At a glance</h2>
              <div class="row g-3">
		<div class="col-6 d-flex align-items-center justify-content-center">
		  <img src="headshot.jpg" alt="Mark Gaultney headshot"
		       class="img-fluid rounded shadow-sm" style="max-height: 200px; object-fit: cover;">
		</div>
                <div class="col-6">
                  <ul class="list-unstyled small mb-0">
                    <li><span class="bullet"></span>Client-first engagement</li>
                    <li><span class="bullet"></span>Clear, written scopes</li>
                    <li><span class="bullet"></span>Simple pricing</li>
                    <li><span class="bullet"></span>Fast, reliable comms</li>
                  </ul>
                </div>
              </div>
              <div class="mt-3"><a href="https://www.linkedin.com/in/mark-gaultney/" class="link-primary" target="_blank" rel="noopener">More background on LinkedIn →</a></div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </header>

  <!-- ABOUT -->
  <section id="about" class="py-5">
    <div class="container">
      <div class="row justify-content-center">
        <div class="col-lg-10">
          <h2 class="section-title h1 mb-4">About Me</h2>
          <p class="lead">I’m <strong>Mark Gaultney</strong>, PMP-certified Project Manager and Manufacturing/Distribution Consultant with over 25 years of experience helping multi-national manufacturers and distributors implement, upgrade, and optimize Oracle JD Edwards and related systems.</p>

          <div class="row g-4">
            <div class="col-md-6">
              <div class="p-4 bg-white border rounded-3 shadow-sm h-100">
                <h3 class="h5">Core Competencies</h3>
                <ul class="mt-2 mb-0">
                  <li>Project & Program Management (PMP since 2001)</li>
                  <li>Manufacturing & Distribution Consulting</li>
                  <li>Business Process Re‑engineering</li>
                  <li>MRP & DRP planning, Product Costing</li>
                  <li>Implementations, Upgrades, Enhancements</li>
                  <li>Advanced Order Configurator, EDI, Barcode/RF Data Collection</li>
                </ul>
              </div>
            </div>
            <div class="col-md-6">
              <div class="p-4 bg-white border rounded-3 shadow-sm h-100">
                <h3 class="h5">Education & Credentials</h3>
                <ul class="mt-2 mb-0">
                  <li>Bachelor’s Degree — University of Georgia</li>
                  <li>Master’s Degree in Project Management — Keller Graduate School of Management</li>
                  <li>Certified Project Management Professional (PMP), PMI</li>
                </ul>
              </div>
            </div>
          </div>

          <div class="row g-4 mt-1">
            <div class="col-12">
              <div class="p-4 bg-white border rounded-3 shadow-sm">
                <h3 class="h5">Experience Highlights</h3>
                <ul class="list-unstyled list-timeline mt-3 mb-0">
                  <li>
                    <div><span class="bullet"></span><strong>Consultant — Chart Industries, LLC</strong> <span class="text-muted">(2018–Present)</span></div>
                    <div class="ms-4 text-muted small">Led EDI setup, Engineer-to-Order implementation, and JDE 9.2 upgrades across multiple facilities.</div>
                  </li>
                  <li>
                    <div><span class="bullet"></span><strong>Manufacturing IT Manager — Trek Bikes, Inc</strong> <span class="text-muted">(2010–2017)</span></div>
                    <div class="ms-4 text-muted small">Directed global system upgrades, distributorship launches in Mexico/Poland, process redesign, and custom application/report development.</div>
                  </li>
                  <li>
                    <div><span class="bullet"></span><strong>Lead Consultant — National Oilwell Varco (NOV)</strong> <span class="text-muted">(2009)</span></div>
                    <div class="ms-4 text-muted small">Guided conversion from legacy systems into JDE 9.0, coordinating across six business units.</div>
                  </li>
                  <li>
                    <div><span class="bullet"></span><strong>Lead Consultant — Cellu Tissue Holdings, Inc.</strong> <span class="text-muted">(2005–2008)</span></div>
                    <div class="ms-4 text-muted small">Implemented full work order system, MRP for 60‑day planning, and real‑time barcode reporting across mills.</div>
                  </li>
                  <li>
                    <div><span class="bullet"></span><strong>Earlier Roles</strong></div>
                    <div class="ms-4 text-muted small">Consulting and leadership positions at Lindt, Flotek Industries, Oxford Industries, SPX Dock Products, Align Technologies, Steel Coil Services, Fintube Technologies, Mayer Electric, International Furniture Designs, and others.</div>
                  </li>
                </ul>
                <div class="mt-3">
                  <a class="btn btn-outline-primary btn-sm" href="https://www.linkedin.com/in/mark-gaultney/" target="_blank" rel="noopener">View complete background on LinkedIn</a>
                </div>
              </div>
            </div>
          </div>

        </div>
      </div>
    </div>
  </section>

  <!-- CONTACT -->
  <section id="contact" class="py-5">
    <div class="container">
      <div class="row justify-content-center">
        <div class="col-lg-8">
          <h2 class="section-title h1 mb-4">Contact Me</h2>
          <p class="text-muted">Prefer LinkedIn? <a href="https://www.linkedin.com/in/mark-gaultney/" target="_blank" rel="noopener">Send a message on LinkedIn</a> — or use the quick form below to start an email to <a href="mailto:mark@gaultneymanagement.com">mark@gaultneymanagement.com</a></p>

          <form id="contactForm" class="row g-3" onsubmit="return handleMailto(event)">
            <div class="col-md-6">
              <label for="name" class="form-label">Your name</label>
              <input type="text" class="form-control" id="name" required>
            </div>
            <div class="col-md-6">
              <label for="email" class="form-label">Your email</label>
              <input type="email" class="form-control" id="email" required>
            </div>
            <div class="col-12">
              <label for="subject" class="form-label">Subject</label>
              <input type="text" class="form-control" id="subject" placeholder="How can I help?" required>
            </div>
            <div class="col-12">
              <label for="message" class="form-label">Message</label>
              <textarea id="message" class="form-control" rows="5" required></textarea>
            </div>
            <div class="col-12 d-flex align-items-center gap-3">
              <button type="submit" class="btn btn-primary">Open Email</button>
              <small class="text-muted">This opens your default mail app with the details pre‑filled.</small>
            </div>
          </form>
        </div>
      </div>
    </div>
  </section>

  <!-- FOOTER -->
  <footer class="py-4 bg-white border-top">
    <div class="container d-flex flex-column flex-lg-row align-items-center justify-content-between gap-2">
      <div class="small">
        © 2025 Copyright: <strong>Mark Gaultney</strong> &nbsp; &amp; Designed by: <a href="https://gaultara.com/" target="_blank" rel="noopener"><strong>Gaultara</strong></a>
      </div>
      <div class="small">
        <a class="small-link" href="https://www.linkedin.com/in/mark-gaultney/" target="_blank" rel="noopener">LinkedIn</a>
      </div>
    </div>
  </footer>

  <script>
    function handleMailto(e){
      e.preventDefault();
      const name = document.getElementById('name').value.trim();
      const from = document.getElementById('email').value.trim();
      const subject = document.getElementById('subject').value.trim();
      const msg = document.getElementById('message').value.trim();

      const lines = [
        `Name: ${name}`,
        `Email: ${from}`,
        '',
        msg
      ];
      const body = encodeURIComponent(lines.join('\n'));
      const mailto = `mailto:mark@gaultneymanagement.com?subject=${encodeURIComponent(subject)}&body=${body}`;
      window.location.href = mailto;
      return false;
    }
  </script>
  <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>

