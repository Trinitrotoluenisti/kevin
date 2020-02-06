var content_row = 1;

function addContent() {
  html = '<div id="content-row">';
  html += '<div class="form-group">';
  html += '<label class="col-sm-2">Page Content</label>';
  html += '<div class="col-sm-10">';
  html +=
    '<textarea class="form-control txtText" id="code_preview' +
    content_row +
    '" name="page_code[' +
    content_row +
    '][code]" style="height: 300px;"></textarea>';
  html += "</div>";
  html += "</div>";
  html += "</div>";
  $("#content-row").append(html);
  $("#code_preview" + content_row).summernote({ height: 300 });

  content_row++;
}
