import requests
import getpass
from bs4 import BeautifulSoup, Comment
import re
import zipfile
import StringIO
import shutil
import os
from glob import glob


class XNATExplorer:
    def __init__(self, xnat_root, project_name, username=None, password=None):
        if username is None:
            username = raw_input('Username: ')
        if password is None:
            password = getpass.getpass()

        if xnat_root[-1] != '/':
            xnat_root = xnat_root + '/'

        self.xnat_root = xnat_root
        self.project_name = project_name.strip()

        self.project_url = self.xnat_root + 'data/archive/projects/' + self.project_name

        with requests.Session() as s:
            if username:
                    s.auth = (username, password)
            self.session = s

        # Test for correct username & password
        result = self.session.get(self.project_url)

        if result.status_code == 401:
            raise ValueError("Wrong username/password combination or you're not authorized to access this project!")
        elif result.status_code == 404:
            raise ValueError("The specified XNAT project doesn't seem to exist, please check the project name!")

        self.subjects_url = self.project_url + '/subjects/'
        return

    def __enter__(self):
        return self

    def __exit__(self, exc_typ, exc_value, traceback):
        self.session.close()


    def get_subjects(self):
        result_json = self.session.get(self.subjects_url).json()

        subjects = result_json['ResultSet']['Result']

        # Sort them
        self.subjects = sorted(subjects, key=lambda k: k['label'])

        return self.subjects

    def get_experiments(self, subject):
        experiments_url = self.subjects_url + subject['label'] + '/experiments'
        result_json = self.session.get(experiments_url).json()

        experiments = result_json['ResultSet']['Result']

        return experiments

    def has_experiment(self, subject, experiment_label, strict_comparison=False):
        experiments = self.get_experiments(subject)
        has_experiment = False

        for i_experiment in experiments:
            if strict_comparison:
                has_experiment = i_experiment['label'] == experiment_label
            else:
                has_experiment = experiment_label in i_experiment['label']

            if has_experiment:
                break

        return has_experiment

    def get_experiment(self, subject, experiment_label, strict_comparison=False):
        experiment = None

        experiments = self.get_experiments(subject)

        for i_experiment in experiments:
            if strict_comparison:
                has_experiment = i_experiment['label'] == experiment_label
            else:
                has_experiment = experiment_label in i_experiment['label']

            if has_experiment:
                experiment = i_experiment
                break

        return experiment


    def get_scans(self, subject, experiment):
        scans_url = self.subjects_url + subject['label'] + '/experiments/' + experiment['ID'] + '/scans/'
        result_json = self.session.get(scans_url).json()

        scans = result_json['ResultSet']['Result']

        return scans

    def find_scan(self, subject, experiment, expression):
        scans = self.get_scans(subject, experiment)

        regex = re.compile(expression)

        matches = [i_scan for i_scan in scans if re.match(regex, i_scan['type'])]

        return matches

    def get_experiment_resource_list(self, subject, experiment, folder_name):
        experiment_uri = self.subjects_url + subject['label'] + '/experiments/' + experiment['ID']
        resource_uri = experiment_uri + '/resources/' + folder_name + '/files/'

        result = self.session.get(resource_uri).json()

        resource_list = result['ResultSet']['Result']

        # Get it sorted based on name
        resource_list = sorted(resource_list, key=lambda k: k['Name'])

        return resource_list

    def get_dicom_tags(self, subject, experiment, scan):
        dicomdump_uri = self.xnat_root + 'REST/services/dicomdump?src='
        scans_url = '/archive/projects/' + self.project_name +'/experiments/' + experiment['ID'] + '/scans/' + scan['ID'] + '&format=json'

        dicomtag_uri = dicomdump_uri + scans_url
        result = self.session.get(dicomtag_uri).json()

        dicom_tags = result['ResultSet']['Result']

        return dicom_tags


    def get_selected_experiment_resource_list(self, subject, experiment, folder_name, search_key):
        experiment_uri = self.subjects_url + subject['label'] + '/experiments/' + experiment['ID']
        resource_uri = experiment_uri + '/resources/' + folder_name + '/files/'

        result = self.session.get(resource_uri).json()

        resource_list = result['ResultSet']['Result']

        selected_resource_list = list()

        for i_resource in resource_list:
            if search_key in i_resource['Name']:
                selected_resource_list.append(i_resource)

        selected_resource_list = sorted(selected_resource_list, key=lambda k: k['Name'])

        return selected_resource_list


    def get_experiment_resource(self, subject, experiment, folder_name, file_name):
        experiment_uri = self.subjects_url + subject['label'] + '/experiments/' + experiment['ID']
        resource_uri = experiment_uri + '/resources/' + folder_name + '/files/' + file_name

        resource = self.session.get(resource_uri).json()

        return resource

    def download_experiment_resource(self, subject, experiment, folder_name, file_name, local_location):
        experiment_uri = self.subjects_url + subject['label'] + '/experiments/' + experiment['ID']
        resource_uri = experiment_uri + '/resources/' + folder_name + '/files/' + file_name

        response = self.session.get(resource_uri, stream=True)

        if response.status_code == 200:
            with open(local_location, 'wb') as f:
                response.raw.decode_content = True
                shutil.copyfileobj(response.raw, f)
        else:
            raise Exception('No such file!')
        return


    def has_resource(self, subject, experiment, scan, resource_name):
        scan_uri = self.subjects_url + subject['label'] + '/experiments/' + experiment['ID'] + '/scans/' + scan['ID']
        resource_uri = scan_uri + '/resources/PROCESSED/files/' + resource_name

        result = self.session.get(resource_uri)

        if result.status_code == 404:
            has_resource = False
        else:
            has_resource = True

        return has_resource

    def has_scan(self, subject, experiment, expression):
        scans = self.get_scans(subject, experiment)
        scan_codes = list()
        for i_scan in scans:
            scan_codes.append(i_scan['ID'])

        regex = re.compile(expression)

        matches = [string for string in scan_codes if re.match(regex, string)]

        if len(matches) > 0:
            has_scan = True
        else:
            has_scan = False

        return has_scan

    def download_scan(self, subject, experiment, scan, local_location):
        scan_folder_uri = self.subjects_url + subject['label'] + '/experiments/' + experiment['ID'] + '/scans/' + scan['ID']
        dicom_uri = scan_folder_uri + '/resources/DICOM/files?format=zip'

        response = self.session.get(dicom_uri, stream=True)
        try:
            z = zipfile.ZipFile(StringIO.StringIO(response.content))
        except:
            return

        if not os.path.exists(local_location):
            os.makedirs(local_location)

        for member in z.namelist():
            filename = os.path.basename(member)
            if not filename:
                continue

            source = z.open(member)
            target = file(os.path.join(local_location, filename), 'wb')
            with source, target:
                shutil.copyfileobj(source, target)
        # z.extractall(local_location)
        return


    def has_resource(self, subject, experiment, scan, resource_name):
        scan_uri = self.subjects_url + subject['label'] + '/experiments/' + experiment['ID'] + '/scans/' + scan['ID']
        resource_uri = scan_uri + '/resources/PROCESSED/files/' + resource_name

        result = self.session.get(resource_uri)

        if result.status_code == 404:
            has_resource = False
        else:
            has_resource = True

        return has_resource

    def has_file(self, subject, folder, file_name):
        subject_uri = self.subjects_url + subject['label']
        file_uri = subject_uri + '/resources/' + folder + '/files/' + file_name

        result = self.session.get(file_uri)

        if result.status_code == 404:
            has_file = False
        else:
            has_file = True

        return has_file



    def upload_file(self, subject, folder_name, file_name, file_location):
        subject_uri = self.subjects_url + subject['label']
        folder_uri = subject_uri + '/resources/' + folder_name + '/'
        self.session.put(folder_uri)

        file_uri = folder_uri + '/files/' + file_name

        upload_file = {'files': open(file_name, 'rb')}
        self.session.put(file_uri, files=upload_file)

        return

    def zipdir(self, path, ziph):
        # ziph is zipfile handle
        for root, dirs, files in os.walk(path):
            for dir_name in dirs:
                files = glob(os.path.join(root, dir_name, '*.dcm'))
                for file_name in files:
                    modality = os.path.basename(os.path.normpath(dir_name))
                    simple_file_name = os.path.basename(os.path.normpath(file_name))
                    ziph.write(file_name, os.path.join(modality, simple_file_name))

    def upload_directory_to_prearchive(self, directory):
        prearchive_url = self.xnat_root + 'data/services/import'
        prearchive_url = prearchive_url + '?dest=/prearchive/projects/' + self.project_name


        zip_file_name = os.path.join(directory, 'image_data.zip')
        zipf = zipfile.ZipFile(zip_file_name, 'w', zipfile.ZIP_DEFLATED)
        self.zipdir(directory, zipf)
        zipf.close()

        upload_file = {'files': open(zip_file_name, 'rb')}
        response = self.session.post(prearchive_url, files=upload_file)



    def archive_session(self):
        prearchive_url = self.xnat_root + 'data/prearchive/projects/' + self.project_name + '?format=json'

        response = self.session.get(prearchive_url).json()
        prearchive_sessions = response['ResultSet']['Result']

        for i_session in prearchive_sessions:
            session_url = self.xnat_root + 'data/prearchive/projects/' + self.project_name + '/' + i_session['timestamp'] + '/' + i_session['folderName']
            bla = self.session.post(session_url + '?action=commit')


    def set_experiment_label(self, subject, experiment, new_label):
        experiment_uri = self.subjects_url + subject['label'] + '/experiments/' + experiment['ID']
        label_uri = experiment_uri + '?label=' + new_label

        self.session.put(label_uri)

        return

    def get_experiment_label(self, subject, experiment):
        experiment_uri = self.subjects_url + subject['label'] + '/experiments/' + experiment['ID']
        label_uri = experiment_uri + '?format=json'

        experiment_info = self.session.get(label_uri).json()
        experiment_info = experiment_info['items']

        for i_info in experiment_info:
            if not i_info['meta']['isHistory']:
                cur_experiment_info = i_info

        experiment_label = cur_experiment_info['data_fields']['label']

        return experiment_label


    def create_scan_folder(self, subject, experiment, scan, folder_name):
        if self.has_scan(subject, experiment, scan['ID']):
            scan_folder_uri = self.subjects_url + subject['label'] + '/experiments/' + experiment['ID'] + '/scans/' + scan['ID']
            self.session.put(scan_folder_uri + '/resources/' + folder_name + '/')
        else:
            raise Exception('Could not create scan folder, scan does not exist!')
        return

    def upload_scan_resource(self, subject, experiment, scan, folder_name, file_name, file_location):
        self.create_scan_folder(subject, experiment, scan, folder_name)

        scan_folder_uri = self.subjects_url + subject['label'] + '/experiments/' + experiment['ID'] + '/scans/' + scan['ID']
        file_uri = scan_folder_uri + '/resources/' + folder_name + '/files/' + file_name

        result = self.session.get(file_uri)

        if result.status_code == 404:
            upload_file = {'files': open(file_location, 'rb')}

            self.session.put(file_uri, files=upload_file)
        return

    def download_scan_resource(self, subject, experiment, scan, folder_name, file_name, local_location):
        scan_folder_uri = self.subjects_url + subject['label'] + '/experiments/' + experiment['ID'] + '/scans/' + scan['ID']
        file_uri = scan_folder_uri + '/resources/' + folder_name + '/files/' + file_name

        response = self.session.get(file_uri, stream=True)

        if response.status_code == 200:
            with open(local_location, 'wb') as f:
                response.raw.decode_content = True
                shutil.copyfileobj(response.raw, f)
        else:
            raise Exception('No such file!')
        return

    def get_scan_resource_list(self, subject, experiment, scan, folder_name):
        scan_folder_uri = self.subjects_url + subject['label'] + '/experiments/' + experiment['ID'] + '/scans/' + scan['ID']
        resource_uri = scan_folder_uri + '/resources/' + folder_name + '/files/'

        result = self.session.get(resource_uri).json()

        resource_list = result['ResultSet']['Result']

        resource_list = sorted(resource_list, key=lambda k: k['Name'])
        return resource_list


    def set_scan_quality(self, subject, experiment, scan, value):
        scan_folder_uri = self.subjects_url + subject['label'] + '/experiments/' + experiment['ID'] + '/scans/' + scan['ID']
        quality_uri = scan_folder_uri + '?xnat:mrScanData/quality=' + value

        self.session.put(quality_uri)

        return

    def get_scan_quality(self, subject, experiment, scan):
        scan_folder_uri = self.subjects_url + subject['label'] + '/experiments/' + experiment['ID'] + '/scans/' + scan['ID']
        quality_uri = scan_folder_uri + '?format=json'

        scan_info = self.session.get(quality_uri).json()
        scan_quality = scan_info['items'][0]['data_fields']['quality']

        return scan_quality

    def delete_scan(self, subject, experiment, scan):
        scan_folder_uri = self.subjects_url + subject['label'] + '/experiments/' + experiment['ID'] + '/scans/' + scan['ID']
        # dicom_uri = scan_folder_uri + '/resources/DICOM?removeFiles=True'
        # snapshot_uri = scan_folder_uri + '/resoures/SNAPSHOTS?removeFiles=True'
        delete_uri = scan_folder_uri + '?removeFiles=True'

        # self.session.delete(dicom_uri)
        # self.session.delete(snapshot_uri)
        self.session.delete(delete_uri)

        return

    def get_experiment_date(self, subject, experiment):
        experiment_uri = self.subjects_url + subject['label'] + '/experiments/' + experiment['ID'] + '?format=json'

        experiment_info = self.session.get(experiment_uri).json()
        try:
            experiment_date = experiment_info['items'][0]['data_fields']['date']
        except KeyError:
            experiment_date = None

        return experiment_date

    def has_mask(self, subject, experiment, scan, suffix):
        scan_folder_uri = self.subjects_url + subject['label'] + '/experiments/' + experiment['ID'] + '/scans/' + scan['ID']
        mask_folder_uri = scan_folder_uri + '/resources/MASKS/files/mask' + suffix + '.nii.gz'

        result = self.session.get(mask_folder_uri)

        if result.status_code == 404:
            has_mask = False
        else:
            has_mask = True

        return has_mask

    def get_gender(self, subject):
        subject_url = self.xnat_root + subject['URI'] + '?format=xml'
        result = self.session.get(subject_url)

        if result.status_code == 200:
            soup = BeautifulSoup(result.text, "lxml")
            gender = soup.find('xnat:gender')
            if gender is None:
                raise Exception('Gender not found!')
            else:
                gender = gender.string
        return gender

    def get_age(self, subject):
        subject_url = self.xnat_root + subject['URI'] + '?format=xml'
        result = self.session.get(subject_url)

        if result.status_code == 200:
            soup = BeautifulSoup(result.text, "lxml")
            age = soup.find('xnat:age')
            if age is None:
                raise Exception('Age not found!')
            else:
                age = age.string

        return age



    def get_scanner(self, subject, experiment):
        experiment_url = self.xnat_root + experiment['URI'] + '?format=xml'
        result = self.session.get(experiment_url)

        if result.status_code == 200:
            soup = BeautifulSoup(result.text, "lxml")
            scanner = soup.find('xnat:scanner')

            scanner_manufacturer = scanner['manufacturer']
            scanner_model = scanner['model']

        return scanner_manufacturer, scanner_model

    def get_acquisition_site(self, subject, experiment):
        experiment_url = self.xnat_root + experiment['URI'] + '?format=xml'
        result = self.session.get(experiment_url)

        if result.status_code == 200:
            soup = BeautifulSoup(result.text, "lxml")
            acquisition_site = soup.find('xnat:acquisition_site')
        if acquisition_site is not None:
            acquisition_site = acquisition_site.string

        return acquisition_site



    def set_gender(self, subject, gender):
        gender = gender.lower()
        if gender.upper() == 'M':
            gender = 'male'
        elif gender.upper() == 'F':
            gender = 'female'

        if gender != 'male' and gender != 'female':
            raise Exception("Gender should be male or female")

        subject_url = self.project_url + '/subjects/' + subject['label']
        gender_url = subject_url + '?gender=' + gender

        self.session.put(gender_url)

        return

    def set_age(self, subject, age):
        age = str(age)

        subject_url = self.project_url + '/subjects/' + subject['label']
        age_url = subject_url + '?age=' + age

        self.session.put(age_url)

        return

    def set_dob(self, subject, dob):
        dob = dob.strftime('%Y-%m-%d')

        subject_url = self.project_url + '/subjects/' + subject['label']
        dob_url = subject_url + '?dob=' + dob

        self.session.put(dob_url)

        return

    def create_subject(self, subject_label):
        subject_url = self.project_url + '/subjects/' + subject_label

        # Check to see if subject exists
        result = self.session.get(subject_url)
        if result.status_code != 200:
            self.session.put(subject_url)

        subjects = self.get_subjects()
        cur_subject = filter(lambda k: k['label'] == subject_label, subjects)[0]

        return cur_subject

    def create_experiment(self, subject, experiment_label, session_type, date):
        # Date is in YY-MM-DD format
        experiment_uri = self.subjects_url + subject['label'] + '/experiments/' + experiment_label
        if session_type == 'MR':
            experiment_uri = experiment_uri + '?xnat:mrSessionData/date=' + date
        elif session_type == 'CT':
            experiment_uri = experiment_uri + '?xnat:ctSessionData/date=' + date
        elif session_type == 'PET':
            experiment_uri = experiment_uri + '?xnat:petSessionData/date=' + date
        elif session_type == 'OTHER':
            experiment_uri = experiment_uri + '?xnat:otherDicomSessionData/date=' +date


        result = self.session.get(experiment_uri)
        if result.status_code != 200:
            self.session.put(experiment_uri)

        experiments = self.get_experiments(subject)
        cur_experiment = filter(lambda k: k['label'] == experiment_label, experiments)[0]

        return cur_experiment


    def create_scan(self, subject, experiment, scan_label, scan_modality, scan_type):
        experiment_uri = self.subjects_url + subject['label'] + '/experiments/' + experiment['label']
        scan_uri = experiment_uri + '/scans/' + scan_label

        if scan_modality == 'MR':
            scan_uri = scan_uri + '?xsiType=xnat:mrScanData&xnat:mrScanData/type=' + scan_type
        elif scan_modality == 'CT':
            scan_uri = scan_uri + '?xsiType=xnat:ctScanData&xnat:ctScanData/type=' + scan_type
        elif scan_modality == 'PET':
            scan_uri = scan_uri + '?xsiType=xnat:petScanData&xnat:petScanData/type=' + scan_type
        elif scan_modality == 'OTHER':
            scan_uri = scan_uri + '?xsiType=xnat:otherDicomScanData&xnat:otherDicomScanData/type=' + scan_type

        result = self.session.get(scan_uri)
        if result.status_code != 200:
            result = self.session.put(scan_uri)

        scans = self.get_scans(subject, experiment)
        cur_scan = filter(lambda k: k['ID'] == scan_label, scans)[0]

        return cur_scan


    def set_custom_field(self, subject, name, value):
        subject_url = self.project_url + '/subjects/' + subject['label']
        field_url = subject_url + "?xnat:subjectData/fields/field[name%3D'" + name + "']/field=" + str(value)

        response = self.session.put(field_url)

        return


    def get_custom_field(self, subject, name):
        subject_url = self.xnat_root + subject['URI'] + '?format=xml'
        result = self.session.get(subject_url)

        if result.status_code == 200:
            soup = BeautifulSoup(result.text, "lxml")
            # Find the tag
            field = soup.find(attrs={'name': name})
            if field is None:
                field_value = None
            else:
                # Remove comment
                field_value = "".join(field.find_all(text=lambda t: not isinstance(t, Comment)))
                field_value = field_value.strip()
        return field_value

    def has_field(self, subject, name):
        subject_url = self.xnat_root + subject['URI'] + '?format=xml'
        result = self.session.get(subject_url)

        if result.status_code == 200:
            soup = BeautifulSoup(result.text, "lxml")
            # Find the tag
            field = soup.find(attrs={'name': name})
            if field is None:
                has_field = False
            else:
                has_field = True

        return has_field
