#define MSG_TO_STRING

#include "vals.h"

#include "Fields.cpp"
#include "MessageInterface.cpp"
#include "ReadBufferSection.cpp"
#include "WriteBufferFixedSize.h"

namespace noec {

namespace msg {

Command cmd;
UpdateHeader uphdr;
UpdateBody<16> upbody;

void clear_values() { upbody.clear_values(); }

void add_values(int idx, int value) {
  static noec::UpdateBody<16>::ValuesEntry entry;
  entry.set_key(idx);
  entry.set_value(value);
  upbody.add_values(entry);
}

int upbody_size() {
  static EmbeddedProto::MessageSizeCalculator msg_size;
  msg_size.clear();
  upbody.serialize(msg_size);
  return msg_size.get_size();
}

EmbeddedProto::WriteBufferFixedSize<256> &serialize() {
  static EmbeddedProto::WriteBufferFixedSize<256> buffer;
  buffer.clear();

  cmd.set_cmd(noec::Command::command::UPDATE);
  cmd.serialize(buffer);

  uphdr.set_numbytes(upbody_size());

  uphdr.serialize(buffer);
  upbody.serialize(buffer);

  return buffer;
}

#ifdef MSG_TO_STRING
char const *to_string() {
  static char str[2048];
  memset(str, '\0', 2048);

  static EmbeddedProto::string_view sv;
  sv.data = &str[0];
  sv.size = 2048;

  sv = cmd.to_string(sv);
  sv = uphdr.to_string(sv);
  upbody.to_string(sv);

  return &str[0];
}
#endif
} // namespace msg

} // namespace noec
