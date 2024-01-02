package storage

import (
	"encoding/binary"
	"encoding/gob"
	"fmt"
	"io"
	"os"
)

type TextStorage struct {
	size uint32
	file *os.File
}

func NewTextStorage() *TextStorage {
	return &TextStorage{}
}

func (s *TextStorage) Load() {
	f, err := os.OpenFile(LINE_PATH, os.O_RDWR|os.O_CREATE, 0644)
	if err != nil {
		panic(err)
	}

	if err = binary.Read(f, binary.NativeEndian, &s.size); err == io.EOF {
		s.size = 0
	} else if err != nil {
		panic(err)
	}
}

func (s *TextStorage) AppendText(text string) error {
	e := gob.NewEncoder(s.file)
	if err := e.Encode(text); err != nil {
		return err
	}
	s.size++
	return nil
}

func (s *TextStorage) openNewFile() error {
	path := fmt.Sprintf("%s/%d.gob", DATA_PATH, storage.size/FILE_SIZE)
	var err error
	s.file, err = os.OpenFile(path, os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0644)
	return err
}
