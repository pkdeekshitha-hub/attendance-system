    async function getMyTasks() {
      try {
        const res = await fetch(BASE_URL + '/api/tasks/my-tasks', {
          headers: { 'Authorization': 'Bearer ' + token }
        });
        const data = await res.json();
        const tbody = document.getElementById('tasksBody');
        if (data.tasks.length === 0) {
          tbody.innerHTML = '<tr><td colspan="4" class="text-center text-muted">No tasks submitted yet</td></tr>';
          return;
        }
        let rows = '';
        data.tasks.forEach(function(t) {
          rows += '<tr><td>' + t.title + '</td><td>' + (t.description || '-') + '</td><td><span class="badge-' + t.status.toLowerCase() + '">' + t.status + '</span></td><td>' + t.submitted_at + '</td></tr>';
        });
        tbody.innerHTML = rows;
      } catch (err) {}
    }
