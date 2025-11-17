// Admin form handler: posts JSON to /admin/add-item

document.addEventListener('DOMContentLoaded', function () {
  var form = document.getElementById('addItemForm');
  var messageEl = document.getElementById('formMessage');

  if (!form) return; // nothing to do

  form.addEventListener('submit', function (e) {
    e.preventDefault();

    var name = document.getElementById('name').value || '';
    var description = document.getElementById('description').value || '';
    var price = document.getElementById('price').value || '';
    var img = document.getElementById('img').value || '';
  var specialday = document.getElementById('specialday') ? document.getElementById('specialday').value : '';

    // Send data to server (no extra client-side validation)
    fetch('/admin/add-item', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name: name, description: description, price: price, img: img, specialday: specialday })
    })
      .then(function (res) {
        // try to parse JSON, otherwise read text
        var c = res.headers.get('content-type') || '';
        if (c.indexOf('application/json') !== -1) return res.json();
        return res.text().then(function (t) { return { message: t }; });
      })
      .then(function (data) {
        if (messageEl) messageEl.innerHTML = '<div class="alert alert-info">' + (data.message || 'Saved') + '</div>';
        form.reset();
      })
      .catch(function (err) {
        console.error('Error adding item:', err);
        if (messageEl) messageEl.innerHTML = '<div class="alert alert-danger">Error adding item</div>';
      });
  });
});
