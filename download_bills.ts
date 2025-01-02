function downloadAttachments() {
  var threads = GmailApp.search('from:Jamaica Public Service Co. Ltd has:attachment');
  var folder = DriveApp.createFolder('JPS Bills');

  threads.forEach(thread => {
    var messages = thread.getMessages();
    messages.forEach(message => {
      var attachments = message.getAttachments();
      attachments.forEach(attachment => {
        // Only save the attachment if it's a PDF file
        if (attachment.getContentType() === 'application/pdf' || attachment.getName().toLowerCase().endsWith('.pdf')) {
          folder.createFile(attachment);
        }
      });
    });
  });
}

