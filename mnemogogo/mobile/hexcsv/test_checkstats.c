#include <stdio.h>
#include <stdlib.h>
#include "hexcsv.h"

#define MAX_ID_LEN 20
#define MAX_DB_SIZE 10000
#define MAX_PATH 255

char ids[MAX_DB_SIZE][MAX_ID_LEN];
int max_id;
int grades[MAX_DB_SIZE];

char filename[MAX_PATH];

char* joinpath(char* path, char* file)
{
    sprintf(filename, "%s%c%s", path, '/', file);
    return filename;
}

void chomp(char* str)
{
    while (*str != '\0' && *str != '\n')
	++str;

    *str = '\0';
}

void show_ids_grades(FILE* f)
{
    int i;
    for (i=0; i < max_id; ++i)
	fprintf(f, "%s %d\n", ids[i], grades[i]);
}

void read_ids(char *path)
{
    int i = 0;
    FILE* f = fopen(joinpath(path, "ids"), "r");
    if (!f) {
	fprintf(stderr, "no ids file!\n");
	exit(1);
    }

    while (fgets(ids[i], MAX_ID_LEN, f)) {
	chomp(ids[i]);
	grades[i] = -1;
	++i;
    }

    max_id = i;
    fclose(f);
}

int id_to_serial(char* id)
{
    int i;

    for (i=0; i < max_id; ++i)
	if (strcmp(ids[i], id) == 0)
	    return i;

    return -1;
}

void read_grades(char* path)
{
    int i = 0;
    char line[BUFSIZ];
    char id[MAX_ID_LEN];
    int serial;
    int grade;
    FILE* f = fopen(joinpath(path, "grades"), "r");

    if (!f) {
	fprintf(stderr, "no grades file!\n");
	exit(1);
    }

    while (fgets(line, BUFSIZ, f)) {
	sscanf(line, "%s %d", &id, &grade);
	serial = id_to_serial(id);
	if (serial >= 0)
	    grades[serial] = grade;
    }

    fclose(f);
}

int main(int argc, char** argv)
{
    int r;
    carddb_t db;
    card_t curr;

    char* srcpath = argv[1];
    char* dstpath = argv[1];

    if (argc < 2) {
	fprintf(stderr, "please specify a sync path\n");
	return -1;
    }

    if (argc > 2)
	dstpath = argv[2];

    read_ids(srcpath);
    read_grades(srcpath);
    show_ids_grades(stdout);

    db = loadcarddb(srcpath, &r);
    if (r < 0) {
	fprintf(stderr, "error: %s\n", errorstr(r));
	return r;
    }
    fprintf(stderr, "assert after load.\n");
    debughexcsv(db, stderr, 0);
    assertinvariants(db);

    buildrevisionqueue(db);
    fprintf(stderr, "assert after buildrevisionqueue.\n");
    debughexcsv(db, stderr, 1);
    assertinvariants(db);

    while (getcard(db, &curr)) {
	//debughexcsv(db, stderr, 0);
	assertinvariants(db);

	if (grades[curr] == -1) {
	    printf("no grade for card %s\n", ids[(int)curr]);
	    processanswer(db, curr, 4, 0);
	} else {
	    processanswer(db, curr, grades[curr], 0);
	    printf("%s: ", ids[(int)curr]);
	    writecard(db, stdout, curr);
	}
    }

    savecarddb(db, dstpath);
    freecarddb(db);
    return 0;
}
