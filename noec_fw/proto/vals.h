/*
 *  This file is generated with Embedded Proto, PLEASE DO NOT EDIT!
 *  source: vals.proto
 */

// This file is generated. Please do not edit!
#ifndef VALS_H
#define VALS_H

#include <cstdint>
#include <MessageInterface.h>
#include <WireFormatter.h>
#include <Fields.h>
#include <MessageSizeCalculator.h>
#include <ReadBufferSection.h>
#include <RepeatedFieldFixedSize.h>
#include <FieldStringBytes.h>
#include <Errors.h>
#include <Defines.h>
#include <limits>

// Include external proto definitions

namespace noec {

class Command final: public ::EmbeddedProto::MessageInterface
{
  public:
    Command() = default;
    Command(const Command& rhs )
    {
      if(rhs.has_cmd())
      {
        set_cmd(rhs.get_cmd());
      }
      else
      {
        clear_cmd();
      }

    }

    Command(const Command&& rhs ) noexcept
    {
      if(rhs.has_cmd())
      {
        set_cmd(rhs.get_cmd());
      }
      else
      {
        clear_cmd();
      }

    }

    ~Command() override = default;

    enum class command : uint32_t
    {
      START = 0,
      END = 1,
      UPDATE = 2
    };

    enum class FieldNumber : uint32_t
    {
      NOT_SET = 0,
      CMD = 1
    };

    Command& operator=(const Command& rhs)
    {
      if(rhs.has_cmd())
      {
        set_cmd(rhs.get_cmd());
      }
      else
      {
        clear_cmd();
      }

      return *this;
    }

    Command& operator=(const Command&& rhs) noexcept
    {
      if(rhs.has_cmd())
      {
        set_cmd(rhs.get_cmd());
      }
      else
      {
        clear_cmd();
      }
      
      return *this;
    }

    static constexpr char const* CMD_NAME = "cmd";
    inline bool has_cmd() const
    {
      return 0 != (presence::mask(presence::fields::CMD) & presence_[presence::index(presence::fields::CMD)]);
    }
    inline void clear_cmd()
    {
      presence_[presence::index(presence::fields::CMD)] &= ~(presence::mask(presence::fields::CMD));
      cmd_.clear();
    }
    inline void set_cmd(const command& value)
    {
      presence_[presence::index(presence::fields::CMD)] |= presence::mask(presence::fields::CMD);
      cmd_ = value;
    }
    inline void set_cmd(const command&& value)
    {
      presence_[presence::index(presence::fields::CMD)] |= presence::mask(presence::fields::CMD);
      cmd_ = value;
    }
    inline const command& get_cmd() const { return cmd_.get(); }
    inline command cmd() const { return cmd_.get(); }


    ::EmbeddedProto::Error serialize(::EmbeddedProto::WriteBufferInterface& buffer) const override
    {
      ::EmbeddedProto::Error return_value = ::EmbeddedProto::Error::NO_ERRORS;

      if(has_cmd() && (::EmbeddedProto::Error::NO_ERRORS == return_value))
      {
        return_value = cmd_.serialize_with_id(static_cast<uint32_t>(FieldNumber::CMD), buffer, true);
      }

      return return_value;
    };

    ::EmbeddedProto::Error deserialize(::EmbeddedProto::ReadBufferInterface& buffer) override
    {
      ::EmbeddedProto::Error return_value = ::EmbeddedProto::Error::NO_ERRORS;
      ::EmbeddedProto::WireFormatter::WireType wire_type = ::EmbeddedProto::WireFormatter::WireType::VARINT;
      uint32_t id_number = 0;
      FieldNumber id_tag = FieldNumber::NOT_SET;

      ::EmbeddedProto::Error tag_value = ::EmbeddedProto::WireFormatter::DeserializeTag(buffer, wire_type, id_number);
      while((::EmbeddedProto::Error::NO_ERRORS == return_value) && (::EmbeddedProto::Error::NO_ERRORS == tag_value))
      {
        id_tag = static_cast<FieldNumber>(id_number);
        switch(id_tag)
        {
          case FieldNumber::CMD:
            presence_[presence::index(presence::fields::CMD)] |= presence::mask(presence::fields::CMD);
            return_value = cmd_.deserialize_check_type(buffer, wire_type);
            break;

          case FieldNumber::NOT_SET:
            return_value = ::EmbeddedProto::Error::INVALID_FIELD_ID;
            break;

          default:
            return_value = skip_unknown_field(buffer, wire_type);
            break;
        }

        if(::EmbeddedProto::Error::NO_ERRORS == return_value)
        {
          // Read the next tag.
          tag_value = ::EmbeddedProto::WireFormatter::DeserializeTag(buffer, wire_type, id_number);
        }
      }

      // When an error was detect while reading the tag but no other errors where found, set it in the return value.
      if((::EmbeddedProto::Error::NO_ERRORS == return_value)
         && (::EmbeddedProto::Error::NO_ERRORS != tag_value)
         && (::EmbeddedProto::Error::END_OF_BUFFER != tag_value)) // The end of the buffer is not an array in this case.
      {
        return_value = tag_value;
      }

      return return_value;
    };

    void clear() override
    {
      clear_cmd();

    }

#ifndef DISABLE_FIELD_NUMBER_TO_NAME 

    static char const* field_number_to_name(const FieldNumber fieldNumber)
    {
      char const* name = nullptr;
      switch(fieldNumber)
      {
        case FieldNumber::CMD:
          name = CMD_NAME;
          break;
        default:
          name = "Invalid FieldNumber";
          break;
      }
      return name;
    }

#endif

#ifdef MSG_TO_STRING

    ::EmbeddedProto::string_view to_string(::EmbeddedProto::string_view& str) const
    {
      return this->to_string(str, 0, nullptr, true);
    }

    ::EmbeddedProto::string_view to_string(::EmbeddedProto::string_view& str, const uint32_t indent_level, char const* name, const bool first_field) const override
    {
      ::EmbeddedProto::string_view left_chars = str;
      int32_t n_chars_used = 0;

      if(!first_field)
      {
        // Add a comma behind the previous field.
        n_chars_used = snprintf(left_chars.data, left_chars.size, ",\n");
        if(0 < n_chars_used)
        {
          // Update the character pointer and characters left in the array.
          left_chars.data += n_chars_used;
          left_chars.size -= n_chars_used;
        }
      }

      if(nullptr != name)
      {
        if( 0 == indent_level)
        {
          n_chars_used = snprintf(left_chars.data, left_chars.size, "\"%s\": {\n", name);
        }
        else
        {
          n_chars_used = snprintf(left_chars.data, left_chars.size, "%*s\"%s\": {\n", indent_level, " ", name);
        }
      }
      else
      {
        if( 0 == indent_level)
        {
          n_chars_used = snprintf(left_chars.data, left_chars.size, "{\n");
        }
        else
        {
          n_chars_used = snprintf(left_chars.data, left_chars.size, "%*s{\n", indent_level, " ");
        }
      }
      
      if(0 < n_chars_used)
      {
        left_chars.data += n_chars_used;
        left_chars.size -= n_chars_used;
      }

      left_chars = cmd_.to_string(left_chars, indent_level + 2, CMD_NAME, true);
  
      if( 0 == indent_level) 
      {
        n_chars_used = snprintf(left_chars.data, left_chars.size, "\n}");
      }
      else 
      {
        n_chars_used = snprintf(left_chars.data, left_chars.size, "\n%*s}", indent_level, " ");
      }

      if(0 < n_chars_used)
      {
        left_chars.data += n_chars_used;
        left_chars.size -= n_chars_used;
      }

      return left_chars;
    }

#endif // End of MSG_TO_STRING

  private:

      // Define constants for tracking the presence of fields.
      // Use a struct to scope the variables from user fields as namespaces are not allowed within classes.
      struct presence
      {
        // An enumeration with all the fields for which presence has to be tracked.
        enum class fields : uint32_t
        {
          CMD
        };

        // The number of fields for which presence has to be tracked.
        static constexpr uint32_t N_FIELDS = 1;

        // Which type are we using to track presence.
        using TYPE = uint32_t;

        // How many bits are there in the presence type.
        static constexpr uint32_t N_BITS = std::numeric_limits<TYPE>::digits;

        // How many variables of TYPE do we need to bit mask all presence fields.
        static constexpr uint32_t SIZE = (N_FIELDS / N_BITS) + ((N_FIELDS % N_BITS) > 0 ? 1 : 0);

        // Obtain the index of a given field in the presence array.
        static constexpr uint32_t index(const fields& field) { return static_cast<uint32_t>(field) / N_BITS; }

        // Obtain the bit mask for the given field assuming we are at the correct index in the presence array.
        static constexpr TYPE mask(const fields& field)
        {
          return static_cast<uint32_t>(0x01) << (static_cast<uint32_t>(field) % N_BITS);
        }
      };

      // Create an array in which the presence flags are stored.
      typename presence::TYPE presence_[presence::SIZE] = {0};

      EmbeddedProto::enumeration<command> cmd_ = static_cast<command>(0);

};

template<
    uint32_t UpdateBody_values_REP_LENGTH
>
class UpdateBody final: public ::EmbeddedProto::MessageInterface
{
  public:
    UpdateBody() = default;
    UpdateBody(const UpdateBody& rhs )
    {
      set_values(rhs.get_values());
    }

    UpdateBody(const UpdateBody&& rhs ) noexcept
    {
      set_values(rhs.get_values());
    }

    ~UpdateBody() override = default;

    class ValuesEntry final: public ::EmbeddedProto::MessageInterface
    {
      public:
        ValuesEntry() = default;
        ValuesEntry(const ValuesEntry& rhs )
        {
          set_key(rhs.get_key());
          set_value(rhs.get_value());
        }

        ValuesEntry(const ValuesEntry&& rhs ) noexcept
        {
          set_key(rhs.get_key());
          set_value(rhs.get_value());
        }

        ~ValuesEntry() override = default;

        enum class FieldNumber : uint32_t
        {
          NOT_SET = 0,
          KEY = 1,
          VALUE = 2
        };

        ValuesEntry& operator=(const ValuesEntry& rhs)
        {
          set_key(rhs.get_key());
          set_value(rhs.get_value());
          return *this;
        }

        ValuesEntry& operator=(const ValuesEntry&& rhs) noexcept
        {
          set_key(rhs.get_key());
          set_value(rhs.get_value());
          return *this;
        }

        static constexpr char const* KEY_NAME = "key";
        inline void clear_key() { key_.clear(); }
        inline void set_key(const int32_t& value) { key_ = value; }
        inline void set_key(const int32_t&& value) { key_ = value; }
        inline int32_t& mutable_key() { return key_.get(); }
        inline const int32_t& get_key() const { return key_.get(); }
        inline int32_t key() const { return key_.get(); }

        static constexpr char const* VALUE_NAME = "value";
        inline void clear_value() { value_.clear(); }
        inline void set_value(const int32_t& value) { value_ = value; }
        inline void set_value(const int32_t&& value) { value_ = value; }
        inline int32_t& mutable_value() { return value_.get(); }
        inline const int32_t& get_value() const { return value_.get(); }
        inline int32_t value() const { return value_.get(); }


        ::EmbeddedProto::Error serialize(::EmbeddedProto::WriteBufferInterface& buffer) const override
        {
          ::EmbeddedProto::Error return_value = ::EmbeddedProto::Error::NO_ERRORS;

          if((0 != key_.get()) && (::EmbeddedProto::Error::NO_ERRORS == return_value))
          {
            return_value = key_.serialize_with_id(static_cast<uint32_t>(FieldNumber::KEY), buffer, false);
          }

          if((0 != value_.get()) && (::EmbeddedProto::Error::NO_ERRORS == return_value))
          {
            return_value = value_.serialize_with_id(static_cast<uint32_t>(FieldNumber::VALUE), buffer, false);
          }

          return return_value;
        };

        ::EmbeddedProto::Error deserialize(::EmbeddedProto::ReadBufferInterface& buffer) override
        {
          ::EmbeddedProto::Error return_value = ::EmbeddedProto::Error::NO_ERRORS;
          ::EmbeddedProto::WireFormatter::WireType wire_type = ::EmbeddedProto::WireFormatter::WireType::VARINT;
          uint32_t id_number = 0;
          FieldNumber id_tag = FieldNumber::NOT_SET;

          ::EmbeddedProto::Error tag_value = ::EmbeddedProto::WireFormatter::DeserializeTag(buffer, wire_type, id_number);
          while((::EmbeddedProto::Error::NO_ERRORS == return_value) && (::EmbeddedProto::Error::NO_ERRORS == tag_value))
          {
            id_tag = static_cast<FieldNumber>(id_number);
            switch(id_tag)
            {
              case FieldNumber::KEY:
                return_value = key_.deserialize_check_type(buffer, wire_type);
                break;

              case FieldNumber::VALUE:
                return_value = value_.deserialize_check_type(buffer, wire_type);
                break;

              case FieldNumber::NOT_SET:
                return_value = ::EmbeddedProto::Error::INVALID_FIELD_ID;
                break;

              default:
                return_value = skip_unknown_field(buffer, wire_type);
                break;
            }

            if(::EmbeddedProto::Error::NO_ERRORS == return_value)
            {
              // Read the next tag.
              tag_value = ::EmbeddedProto::WireFormatter::DeserializeTag(buffer, wire_type, id_number);
            }
          }

          // When an error was detect while reading the tag but no other errors where found, set it in the return value.
          if((::EmbeddedProto::Error::NO_ERRORS == return_value)
             && (::EmbeddedProto::Error::NO_ERRORS != tag_value)
             && (::EmbeddedProto::Error::END_OF_BUFFER != tag_value)) // The end of the buffer is not an array in this case.
          {
            return_value = tag_value;
          }

          return return_value;
        };

        void clear() override
        {
          clear_key();
          clear_value();

        }

    #ifndef DISABLE_FIELD_NUMBER_TO_NAME 

        static char const* field_number_to_name(const FieldNumber fieldNumber)
        {
          char const* name = nullptr;
          switch(fieldNumber)
          {
            case FieldNumber::KEY:
              name = KEY_NAME;
              break;
            case FieldNumber::VALUE:
              name = VALUE_NAME;
              break;
            default:
              name = "Invalid FieldNumber";
              break;
          }
          return name;
        }

    #endif

    #ifdef MSG_TO_STRING

        ::EmbeddedProto::string_view to_string(::EmbeddedProto::string_view& str) const
        {
          return this->to_string(str, 0, nullptr, true);
        }

        ::EmbeddedProto::string_view to_string(::EmbeddedProto::string_view& str, const uint32_t indent_level, char const* name, const bool first_field) const override
        {
          ::EmbeddedProto::string_view left_chars = str;
          int32_t n_chars_used = 0;

          if(!first_field)
          {
            // Add a comma behind the previous field.
            n_chars_used = snprintf(left_chars.data, left_chars.size, ",\n");
            if(0 < n_chars_used)
            {
              // Update the character pointer and characters left in the array.
              left_chars.data += n_chars_used;
              left_chars.size -= n_chars_used;
            }
          }

          if(nullptr != name)
          {
            if( 0 == indent_level)
            {
              n_chars_used = snprintf(left_chars.data, left_chars.size, "\"%s\": {\n", name);
            }
            else
            {
              n_chars_used = snprintf(left_chars.data, left_chars.size, "%*s\"%s\": {\n", indent_level, " ", name);
            }
          }
          else
          {
            if( 0 == indent_level)
            {
              n_chars_used = snprintf(left_chars.data, left_chars.size, "{\n");
            }
            else
            {
              n_chars_used = snprintf(left_chars.data, left_chars.size, "%*s{\n", indent_level, " ");
            }
          }
          
          if(0 < n_chars_used)
          {
            left_chars.data += n_chars_used;
            left_chars.size -= n_chars_used;
          }

          left_chars = key_.to_string(left_chars, indent_level + 2, KEY_NAME, true);
          left_chars = value_.to_string(left_chars, indent_level + 2, VALUE_NAME, false);
      
          if( 0 == indent_level) 
          {
            n_chars_used = snprintf(left_chars.data, left_chars.size, "\n}");
          }
          else 
          {
            n_chars_used = snprintf(left_chars.data, left_chars.size, "\n%*s}", indent_level, " ");
          }

          if(0 < n_chars_used)
          {
            left_chars.data += n_chars_used;
            left_chars.size -= n_chars_used;
          }

          return left_chars;
        }

    #endif // End of MSG_TO_STRING

      private:


          EmbeddedProto::int32 key_ = 0;
          EmbeddedProto::int32 value_ = 0;

    };

    enum class FieldNumber : uint32_t
    {
      NOT_SET = 0,
      VALUES = 1
    };

    UpdateBody& operator=(const UpdateBody& rhs)
    {
      set_values(rhs.get_values());
      return *this;
    }

    UpdateBody& operator=(const UpdateBody&& rhs) noexcept
    {
      set_values(rhs.get_values());
      return *this;
    }

    static constexpr char const* VALUES_NAME = "values";
    inline const ValuesEntry& values(uint32_t index) const { return values_[index]; }
    inline void clear_values() { values_.clear(); }
    inline void set_values(uint32_t index, const ValuesEntry& value) { values_.set(index, value); }
    inline void set_values(uint32_t index, const ValuesEntry&& value) { values_.set(index, value); }
    inline void set_values(const ::EmbeddedProto::RepeatedFieldFixedSize<ValuesEntry, UpdateBody_values_REP_LENGTH>& values) { values_ = values; }
    inline void add_values(const ValuesEntry& value) { values_.add(value); }
    inline ::EmbeddedProto::RepeatedFieldFixedSize<ValuesEntry, UpdateBody_values_REP_LENGTH>& mutable_values() { return values_; }
    inline ValuesEntry& mutable_values(uint32_t index) { return values_[index]; }
    inline const ::EmbeddedProto::RepeatedFieldFixedSize<ValuesEntry, UpdateBody_values_REP_LENGTH>& get_values() const { return values_; }
    inline const ::EmbeddedProto::RepeatedFieldFixedSize<ValuesEntry, UpdateBody_values_REP_LENGTH>& values() const { return values_; }


    ::EmbeddedProto::Error serialize(::EmbeddedProto::WriteBufferInterface& buffer) const override
    {
      ::EmbeddedProto::Error return_value = ::EmbeddedProto::Error::NO_ERRORS;

      if(::EmbeddedProto::Error::NO_ERRORS == return_value)
      {
        return_value = values_.serialize_with_id(static_cast<uint32_t>(FieldNumber::VALUES), buffer, false);
      }

      return return_value;
    };

    ::EmbeddedProto::Error deserialize(::EmbeddedProto::ReadBufferInterface& buffer) override
    {
      ::EmbeddedProto::Error return_value = ::EmbeddedProto::Error::NO_ERRORS;
      ::EmbeddedProto::WireFormatter::WireType wire_type = ::EmbeddedProto::WireFormatter::WireType::VARINT;
      uint32_t id_number = 0;
      FieldNumber id_tag = FieldNumber::NOT_SET;

      ::EmbeddedProto::Error tag_value = ::EmbeddedProto::WireFormatter::DeserializeTag(buffer, wire_type, id_number);
      while((::EmbeddedProto::Error::NO_ERRORS == return_value) && (::EmbeddedProto::Error::NO_ERRORS == tag_value))
      {
        id_tag = static_cast<FieldNumber>(id_number);
        switch(id_tag)
        {
          case FieldNumber::VALUES:
            return_value = values_.deserialize_check_type(buffer, wire_type);
            break;

          case FieldNumber::NOT_SET:
            return_value = ::EmbeddedProto::Error::INVALID_FIELD_ID;
            break;

          default:
            return_value = skip_unknown_field(buffer, wire_type);
            break;
        }

        if(::EmbeddedProto::Error::NO_ERRORS == return_value)
        {
          // Read the next tag.
          tag_value = ::EmbeddedProto::WireFormatter::DeserializeTag(buffer, wire_type, id_number);
        }
      }

      // When an error was detect while reading the tag but no other errors where found, set it in the return value.
      if((::EmbeddedProto::Error::NO_ERRORS == return_value)
         && (::EmbeddedProto::Error::NO_ERRORS != tag_value)
         && (::EmbeddedProto::Error::END_OF_BUFFER != tag_value)) // The end of the buffer is not an array in this case.
      {
        return_value = tag_value;
      }

      return return_value;
    };

    void clear() override
    {
      clear_values();

    }

#ifndef DISABLE_FIELD_NUMBER_TO_NAME 

    static char const* field_number_to_name(const FieldNumber fieldNumber)
    {
      char const* name = nullptr;
      switch(fieldNumber)
      {
        case FieldNumber::VALUES:
          name = VALUES_NAME;
          break;
        default:
          name = "Invalid FieldNumber";
          break;
      }
      return name;
    }

#endif

#ifdef MSG_TO_STRING

    ::EmbeddedProto::string_view to_string(::EmbeddedProto::string_view& str) const
    {
      return this->to_string(str, 0, nullptr, true);
    }

    ::EmbeddedProto::string_view to_string(::EmbeddedProto::string_view& str, const uint32_t indent_level, char const* name, const bool first_field) const override
    {
      ::EmbeddedProto::string_view left_chars = str;
      int32_t n_chars_used = 0;

      if(!first_field)
      {
        // Add a comma behind the previous field.
        n_chars_used = snprintf(left_chars.data, left_chars.size, ",\n");
        if(0 < n_chars_used)
        {
          // Update the character pointer and characters left in the array.
          left_chars.data += n_chars_used;
          left_chars.size -= n_chars_used;
        }
      }

      if(nullptr != name)
      {
        if( 0 == indent_level)
        {
          n_chars_used = snprintf(left_chars.data, left_chars.size, "\"%s\": {\n", name);
        }
        else
        {
          n_chars_used = snprintf(left_chars.data, left_chars.size, "%*s\"%s\": {\n", indent_level, " ", name);
        }
      }
      else
      {
        if( 0 == indent_level)
        {
          n_chars_used = snprintf(left_chars.data, left_chars.size, "{\n");
        }
        else
        {
          n_chars_used = snprintf(left_chars.data, left_chars.size, "%*s{\n", indent_level, " ");
        }
      }
      
      if(0 < n_chars_used)
      {
        left_chars.data += n_chars_used;
        left_chars.size -= n_chars_used;
      }

      left_chars = values_.to_string(left_chars, indent_level + 2, VALUES_NAME, true);
  
      if( 0 == indent_level) 
      {
        n_chars_used = snprintf(left_chars.data, left_chars.size, "\n}");
      }
      else 
      {
        n_chars_used = snprintf(left_chars.data, left_chars.size, "\n%*s}", indent_level, " ");
      }

      if(0 < n_chars_used)
      {
        left_chars.data += n_chars_used;
        left_chars.size -= n_chars_used;
      }

      return left_chars;
    }

#endif // End of MSG_TO_STRING

  private:


      ::EmbeddedProto::RepeatedFieldFixedSize<ValuesEntry, UpdateBody_values_REP_LENGTH> values_;

};

class UpdateHeader final: public ::EmbeddedProto::MessageInterface
{
  public:
    UpdateHeader() = default;
    UpdateHeader(const UpdateHeader& rhs )
    {
      set_numbytes(rhs.get_numbytes());
    }

    UpdateHeader(const UpdateHeader&& rhs ) noexcept
    {
      set_numbytes(rhs.get_numbytes());
    }

    ~UpdateHeader() override = default;

    enum class FieldNumber : uint32_t
    {
      NOT_SET = 0,
      NUMBYTES = 1
    };

    UpdateHeader& operator=(const UpdateHeader& rhs)
    {
      set_numbytes(rhs.get_numbytes());
      return *this;
    }

    UpdateHeader& operator=(const UpdateHeader&& rhs) noexcept
    {
      set_numbytes(rhs.get_numbytes());
      return *this;
    }

    static constexpr char const* NUMBYTES_NAME = "numbytes";
    inline void clear_numbytes() { numbytes_.clear(); }
    inline void set_numbytes(const int32_t& value) { numbytes_ = value; }
    inline void set_numbytes(const int32_t&& value) { numbytes_ = value; }
    inline int32_t& mutable_numbytes() { return numbytes_.get(); }
    inline const int32_t& get_numbytes() const { return numbytes_.get(); }
    inline int32_t numbytes() const { return numbytes_.get(); }


    ::EmbeddedProto::Error serialize(::EmbeddedProto::WriteBufferInterface& buffer) const override
    {
      ::EmbeddedProto::Error return_value = ::EmbeddedProto::Error::NO_ERRORS;

      if((0 != numbytes_.get()) && (::EmbeddedProto::Error::NO_ERRORS == return_value))
      {
        return_value = numbytes_.serialize_with_id(static_cast<uint32_t>(FieldNumber::NUMBYTES), buffer, false);
      }

      return return_value;
    };

    ::EmbeddedProto::Error deserialize(::EmbeddedProto::ReadBufferInterface& buffer) override
    {
      ::EmbeddedProto::Error return_value = ::EmbeddedProto::Error::NO_ERRORS;
      ::EmbeddedProto::WireFormatter::WireType wire_type = ::EmbeddedProto::WireFormatter::WireType::VARINT;
      uint32_t id_number = 0;
      FieldNumber id_tag = FieldNumber::NOT_SET;

      ::EmbeddedProto::Error tag_value = ::EmbeddedProto::WireFormatter::DeserializeTag(buffer, wire_type, id_number);
      while((::EmbeddedProto::Error::NO_ERRORS == return_value) && (::EmbeddedProto::Error::NO_ERRORS == tag_value))
      {
        id_tag = static_cast<FieldNumber>(id_number);
        switch(id_tag)
        {
          case FieldNumber::NUMBYTES:
            return_value = numbytes_.deserialize_check_type(buffer, wire_type);
            break;

          case FieldNumber::NOT_SET:
            return_value = ::EmbeddedProto::Error::INVALID_FIELD_ID;
            break;

          default:
            return_value = skip_unknown_field(buffer, wire_type);
            break;
        }

        if(::EmbeddedProto::Error::NO_ERRORS == return_value)
        {
          // Read the next tag.
          tag_value = ::EmbeddedProto::WireFormatter::DeserializeTag(buffer, wire_type, id_number);
        }
      }

      // When an error was detect while reading the tag but no other errors where found, set it in the return value.
      if((::EmbeddedProto::Error::NO_ERRORS == return_value)
         && (::EmbeddedProto::Error::NO_ERRORS != tag_value)
         && (::EmbeddedProto::Error::END_OF_BUFFER != tag_value)) // The end of the buffer is not an array in this case.
      {
        return_value = tag_value;
      }

      return return_value;
    };

    void clear() override
    {
      clear_numbytes();

    }

#ifndef DISABLE_FIELD_NUMBER_TO_NAME 

    static char const* field_number_to_name(const FieldNumber fieldNumber)
    {
      char const* name = nullptr;
      switch(fieldNumber)
      {
        case FieldNumber::NUMBYTES:
          name = NUMBYTES_NAME;
          break;
        default:
          name = "Invalid FieldNumber";
          break;
      }
      return name;
    }

#endif

#ifdef MSG_TO_STRING

    ::EmbeddedProto::string_view to_string(::EmbeddedProto::string_view& str) const
    {
      return this->to_string(str, 0, nullptr, true);
    }

    ::EmbeddedProto::string_view to_string(::EmbeddedProto::string_view& str, const uint32_t indent_level, char const* name, const bool first_field) const override
    {
      ::EmbeddedProto::string_view left_chars = str;
      int32_t n_chars_used = 0;

      if(!first_field)
      {
        // Add a comma behind the previous field.
        n_chars_used = snprintf(left_chars.data, left_chars.size, ",\n");
        if(0 < n_chars_used)
        {
          // Update the character pointer and characters left in the array.
          left_chars.data += n_chars_used;
          left_chars.size -= n_chars_used;
        }
      }

      if(nullptr != name)
      {
        if( 0 == indent_level)
        {
          n_chars_used = snprintf(left_chars.data, left_chars.size, "\"%s\": {\n", name);
        }
        else
        {
          n_chars_used = snprintf(left_chars.data, left_chars.size, "%*s\"%s\": {\n", indent_level, " ", name);
        }
      }
      else
      {
        if( 0 == indent_level)
        {
          n_chars_used = snprintf(left_chars.data, left_chars.size, "{\n");
        }
        else
        {
          n_chars_used = snprintf(left_chars.data, left_chars.size, "%*s{\n", indent_level, " ");
        }
      }
      
      if(0 < n_chars_used)
      {
        left_chars.data += n_chars_used;
        left_chars.size -= n_chars_used;
      }

      left_chars = numbytes_.to_string(left_chars, indent_level + 2, NUMBYTES_NAME, true);
  
      if( 0 == indent_level) 
      {
        n_chars_used = snprintf(left_chars.data, left_chars.size, "\n}");
      }
      else 
      {
        n_chars_used = snprintf(left_chars.data, left_chars.size, "\n%*s}", indent_level, " ");
      }

      if(0 < n_chars_used)
      {
        left_chars.data += n_chars_used;
        left_chars.size -= n_chars_used;
      }

      return left_chars;
    }

#endif // End of MSG_TO_STRING

  private:


      EmbeddedProto::int32 numbytes_ = 0;

};

} // End of namespace noec
#endif // VALS_H