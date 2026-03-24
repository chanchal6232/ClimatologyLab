import re
import os

filepath = r'c:\Users\Gourav\OneDrive\Desktop\Internship IITR\Lab\dashboard\templates\dashboard\home.html'

with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Fix journal_count
content = re.sub(r'\{\{\s*journal_count\s*\}\}', '{{ journal_count }}', content, flags=re.DOTALL)
content = re.sub(r'\{\{\s*conference_count\s*\}\}', '{{ conference_count }}', content, flags=re.DOTALL)
content = re.sub(r'\{\{\s*book_count\s*\}\}', '{{ book_count }}', content, flags=re.DOTALL)
content = re.sub(r'\{\{\s*book_guideline_count\s*\}\}', '{{ book_guideline_count }}', content, flags=re.DOTALL)
content = re.sub(r'\{\{\s*other_count\s*\}\}', '{{ other_count }}', content, flags=re.DOTALL)

# Let's just fix the specific spans to be safe
patterns = [
    r'px-3"\}\}\{\{\s*journal_count\s*\}\}</span>',
    r'px-3"\}\}\{\{\s*conference_count\s*\}\}</span>',
    # wait, the patterns in the file looks different in view_file
]

# Alternative: Replace the whole block of rows
rows_content = """                        <!-- JOURNAL ARTICLES -->
                        <tr>
                            <td class="py-3">
                                <div class="fw-700">Journal Articles</div>
                                <small class="text-muted">Academic peer-reviewed papers</small>
                            </td>
                            <td class="text-center py-3"><span class="badge bg-primary-subtle text-primary rounded-pill px-3">{{ journal_count }}</span></td>
                            <td class="text-end py-3">
                                <a href="{% url 'dashboard:publication_create' %}?category=journal" class="btn btn-sm btn-light border px-3 me-2" title="Add"><i class="bi bi-plus-lg text-success me-1"></i>Add</a>
                                <a href="{% url 'dashboard:publications_list' %}?category=journal" class="btn btn-sm btn-light border px-3" title="Manage"><i class="bi bi-pencil-square text-primary me-1"></i>Manage</a>
                            </td>
                        </tr>

                        <!-- CONFERENCE PAPERS -->
                        <tr>
                            <td class="py-3">
                                <div class="fw-700">Conference Papers</div>
                                <small class="text-muted">Proceedings and presentations</small>
                            </td>
                            <td class="text-center py-3"><span class="badge bg-primary-subtle text-primary rounded-pill px-3">{{ conference_count }}</span></td>
                            <td class="text-end py-3">
                                <a href="{% url 'dashboard:publication_create' %}?category=conference" class="btn btn-sm btn-light border px-3 me-2" title="Add"><i class="bi bi-plus-lg text-success me-1"></i>Add</a>
                                <a href="{% url 'dashboard:publications_list' %}?category=conference" class="btn btn-sm btn-light border px-3" title="Manage"><i class="bi bi-pencil-square text-primary me-1"></i>Manage</a>
                            </td>
                        </tr>

                        <!-- BOOK CHAPTERS -->
                        <tr>
                            <td class="py-3">
                                <div class="fw-700">Book Chapters</div>
                                <small class="text-muted">Authored or edited sections</small>
                            </td>
                            <td class="text-center py-3"><span class="badge bg-primary-subtle text-primary rounded-pill px-3">{{ book_count }}</span></td>
                            <td class="text-end py-3">
                                <a href="{% url 'dashboard:publication_create' %}?category=book" class="btn btn-sm btn-light border px-3 me-2" title="Add"><i class="bi bi-plus-lg text-success me-1"></i>Add</a>
                                <a href="{% url 'dashboard:publications_list' %}?category=book" class="btn btn-sm btn-light border px-3" title="Manage"><i class="bi bi-pencil-square text-primary me-1"></i>Manage</a>
                            </td>
                        </tr>

                        <!-- BOOKS (Guidelines/Full Books) -->
                        <tr>
                            <td class="py-3">
                                <div class="fw-700">Books</div>
                                <small class="text-muted">Complete monographs or guidelines</small>
                            </td>
                            <td class="text-center py-3"><span class="badge bg-primary-subtle text-primary rounded-pill px-3">{{ book_guideline_count }}</span></td>
                            <td class="text-end py-3">
                                <a href="{% url 'dashboard:publication_create' %}?category=guideline" class="btn btn-sm btn-light border px-3 me-2" title="Add"><i class="bi bi-plus-lg text-success me-1"></i>Add</a>
                                <a href="{% url 'dashboard:publications_list' %}?category=guideline" class="btn btn-sm btn-light border px-3" title="Manage"><i class="bi bi-pencil-square text-primary me-1"></i>Manage</a>
                            </td>
                        </tr>

                        <!-- OTHER DOCUMENTS -->
                        <tr>
                            <td class="py-3">
                                <div class="fw-700">Other Documents</div>
                                <small class="text-muted">Theses, reports, and miscellaneous</small>
                            </td>
                            <td class="text-center py-3"><span class="badge bg-primary-subtle text-primary rounded-pill px-3">{{ other_count }}</span></td>
                            <td class="text-end py-3">
                                <a href="{% url 'dashboard:publication_create' %}?category=other" class="btn btn-sm btn-light border px-3 me-2" title="Add"><i class="bi bi-plus-lg text-success me-1"></i>Add</a>
                                <a href="{% url 'dashboard:publications_list' %}?category=other" class="btn btn-sm btn-light border px-3" title="Manage"><i class="bi bi-pencil-square text-primary me-1"></i>Manage</a>
                            </td>
                        </tr>"""

# Use a regex to replace the entire tbody content
content = re.sub(r'<tbody>.*?</tbody>', f'<tbody>\n{rows_content}\n                    </tbody>', content, flags=re.DOTALL)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)
